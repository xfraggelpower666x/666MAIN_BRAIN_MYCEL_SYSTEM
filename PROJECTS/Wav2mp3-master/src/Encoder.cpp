/******************************************************************************
 * @author Assen Kirov                                                        *
 ******************************************************************************/
#include <sstream>
#include <cstdlib>
#include <vector>
#include <pthread.h>
#include "Encoder.h"
#include "Log.h"

using namespace wav2mp3;


Encoder::Encoder( shared_ptr<WavFile> wavFilePtr ):
        mWavFilePtr(wavFilePtr),
        mMp3Uri(),
        mLameContext(NULL),
        mMp3File()
{
}


Encoder::~Encoder()
{
    // Close mp3 file if open
    if( mMp3File.is_open() ) mMp3File.close();

    // Free memory resources if still allocated
    if( mLameContext ) lame_close(mLameContext);
}


/**
 * @param[in] fname full file URI
 * @return file URI without (last) extension, if any
 */
std::string Encoder::getBaseFileUri( const std::string& fname )
{
    size_t fslashp = fname.rfind('/');
    size_t bslashp = fname.rfind('\\');
    size_t slashp = 0;

    if( fslashp != std::string::npos  &&  bslashp != std::string::npos )
        slashp = std::max(fslashp, bslashp);
    else if( fslashp != std::string::npos )
        slashp = fslashp;
    else if( bslashp != std::string::npos )
        slashp = bslashp;

    return fname.substr(0, slashp) + fname.substr(slashp, fname.rfind('.')-slashp);
}


std::string Encoder::int2str(int i)
{
#if defined(__GXX_EXPERIMENTAL_CXX0X) || __cplusplus >= 201103L
    return std::to_string(i);
#else
    std::ostringstream ss;
    ss << i;
    return ss.str();
#endif  // c++11
}


/**
 * Returns the closest bigger standard rate to the argument (or exact value)
 *
 * @param[in] brate calculated Kbrate
 * @return the closest bigger standard rate (if no exact match)
 */
int Encoder::getStdBRate(int brate)
{
    static const int rates[]={8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128,
                              144, 160, 192, 224, 256, 320};
    static const size_t len = sizeof(rates)/sizeof(int);

    if( brate <= rates[0] ) return rates[0];
    if( brate >= rates[len-1] ) return rates[len-1];

    // Binary search
    int beg=0, end=len-1, i;
    while( end > beg )
    {
        i = beg + (end-beg)/2;

        if( brate == rates[i] )
            break;
        else if( brate > rates[i] )
            beg = i+1;
        else
            end = i;
    }

    if( end > beg )
        return rates[i];
    else
        return rates[end];
}


int Encoder::encode()
{
    LOG("Thread " << pthread_self() << " is encoding '" << mWavFilePtr->getURI() <<
            "'" << std::endl);

    int chunkNum=0;
    bool success=true;
    while( mWavFilePtr->findNextWavChunk() )
    {
        // Set mMp3Uri
        std::string wavUriNoExt = getBaseFileUri(mWavFilePtr->getURI());
        if( chunkNum )
            mMp3Uri = wavUriNoExt + int2str(chunkNum) + ".mp3";
        else
            mMp3Uri = wavUriNoExt + ".mp3";
        //LOG("Encoding '" << mMp3Uri << "'" << std::endl);

        // Initialize LAME lib
        mLameContext = lame_init();
        if( NULL == mLameContext )
        {
            LOG("ERROR in lame_init()" << std::endl);
            success = false;
            break;
        }

        // Set encoding parameters
        if( lame_set_num_channels(mLameContext, mWavFilePtr->getNumChannels()) < 0 ||
            lame_set_in_samplerate(mLameContext, mWavFilePtr->getSampleRate()) < 0 ||
            lame_set_brate(mLameContext,
                           getStdBRate(mWavFilePtr->getByteRate()/1000)) < 0 ||
            lame_set_quality(mLameContext, 5) < 0 ||
            lame_set_mode(mLameContext,
                          mWavFilePtr->getNumChannels() == 1 ? MONO : STEREO) < 0 ||
            lame_set_bWriteVbrTag(mLameContext, 0) < 0 ||
            lame_init_params(mLameContext) != 0 )
        {
            LOG("ERROR setting LAME parameters" << std::endl);
            success = false;
            lame_close(mLameContext); mLameContext = NULL;
            break;
        }

        // Allocate mp3 buffer. Will be freed when the vector goes out of scope.
        int numSamples = mWavFilePtr->getRawAudioDataSize() / mWavFilePtr->getFrameSize();
        size_t mp3bufsz = numSamples*5/4 + 7200;  // According to LAME lib
        std::vector<unsigned char> mp3BufVec;
        try {
            mp3BufVec.resize(mp3bufsz);
        } catch(...) {
            LOG("ERROR allocating mp3 buffer" << std::endl);
            success = false;
            lame_close(mLameContext); mLameContext = NULL;
            break;
        }
        unsigned char* mMp3Buffer = &mp3BufVec[0];

        // Encode PCM data in mp3
        uint16_t bps = mWavFilePtr->getBitsPerSample();
        int encoded=-5;
        if( mWavFilePtr->getNumChannels() == 1 )  // mono
        {
            if( (8 == bps) && (1 == mWavFilePtr->getFrameSize()) )
            {
                // Allocate temp conversion buffer
                uint32_t datasz = mWavFilePtr->getRawAudioDataSize();
                std::vector<short int> copiedDataLVec;
                try {
                    copiedDataLVec.resize(datasz);
                } catch(...) {
                    LOG("ERROR allocating copiedDataLVec" << std::endl);
                    success = false;
                    lame_close(mLameContext); mLameContext = NULL;
                    break;
                }

                // Copy data in 16-bit buffer mCopiedDataL, converting to signed
                const uint8_t* datap =
                    reinterpret_cast<const uint8_t*>(mWavFilePtr->getRawAudioDataPtr());
                for( uint32_t i=0; i<datasz; i++ )
                    copiedDataLVec[i] =
                        static_cast<short int>((static_cast<int>(datap[i]) - 128) * 256);

                encoded = lame_encode_buffer(mLameContext, &copiedDataLVec[0],
                        NULL, numSamples, mMp3Buffer, mp3bufsz);
            }
            else if( (16 == bps) || ((8 == bps) && (2 == mWavFilePtr->getFrameSize())) )
            {
                encoded = lame_encode_buffer(mLameContext,
                        (short int *) mWavFilePtr->getRawAudioDataPtr(),
                        NULL, numSamples, mMp3Buffer, mp3bufsz);
            }
            else if( (24 == bps) && (3 == mWavFilePtr->getFrameSize()) )
            {
                // Allocate temp conversion buffer
                uint32_t datasz = mWavFilePtr->getRawAudioDataSize();
                std::vector<int> copiedDataLVec;
                try {
                    copiedDataLVec.resize(datasz/3);
                } catch(...) {
                    LOG("ERROR allocating copiedDataLVec" << std::endl);
                    success = false;
                    lame_close(mLameContext); mLameContext = NULL;
                    break;
                }

                // Sign-extend little-endian 24-bit samples to 32 bits.
                const uint8_t* datap =
                    reinterpret_cast<const uint8_t*>(mWavFilePtr->getRawAudioDataPtr());
                for( uint32_t i=0, j=0; i<datasz; i += 3, j++ )
                {
                    uint32_t sample = static_cast<uint32_t>(datap[i]) |
                                      (static_cast<uint32_t>(datap[i+1]) << 8) |
                                      (static_cast<uint32_t>(datap[i+2]) << 16);
                    if( sample & 0x800000u )
                        copiedDataLVec[j] = static_cast<int>(sample) - 0x1000000;
                    else
                        copiedDataLVec[j] = static_cast<int>(sample);
                }

                encoded = lame_encode_buffer_int(mLameContext, &copiedDataLVec[0],
                        NULL, numSamples, mMp3Buffer, mp3bufsz);
            }
            else if( (32 == bps) || ((24 == bps) && (4 == mWavFilePtr->getFrameSize())) )
            {
                encoded = lame_encode_buffer_int(mLameContext,
                        (int *) mWavFilePtr->getRawAudioDataPtr(),
                        NULL, numSamples, mMp3Buffer, mp3bufsz);
            }
        }
        else  // 2-channel stereo
        {
            if( (8 == bps) && (2 == mWavFilePtr->getFrameSize()) )
            {
                // Allocate temp conversion buffers
                uint32_t datasz = mWavFilePtr->getRawAudioDataSize();
                std::vector<uint8_t> copiedDataLVec;
                std::vector<uint8_t> copiedDataRVec;
                try {
                    copiedDataLVec.resize(datasz/2);
                    copiedDataRVec.resize(datasz/2);
                } catch(...) {
                    LOG("ERROR allocating copiedDataLVec or copiedDataRVec" << std::endl);
                    success = false;
                    lame_close(mLameContext); mLameContext = NULL;
                    break;
                }

                // Copy data in 16-bit buffers, converting to signed
                const uint8_t* datap =
                    reinterpret_cast<const uint8_t*>(mWavFilePtr->getRawAudioDataPtr());
                for( uint32_t i=0, l=0, r=0; i<datasz; i += 2 )
                {
                    copiedDataLVec[l++] =
                        static_cast<short int>((static_cast<int>(datap[i]) - 128) * 256);
                    copiedDataRVec[r++] =
                        static_cast<short int>((static_cast<int>(datap[i+1]) - 128) * 256);
                }

                encoded = lame_encode_buffer(mLameContext, &copiedDataLVec[0],
                        &copiedDataRVec[0], numSamples, mMp3Buffer, mp3bufsz);
            }
            else if( (16 == bps) || ((8 == bps) && (4 == mWavFilePtr->getFrameSize())) )
            {
                encoded = lame_encode_buffer_interleaved(mLameContext,
                        (short int *) mWavFilePtr->getRawAudioDataPtr(),
                        numSamples, mMp3Buffer, mp3bufsz);
            }
            else if( (24 == bps) && (6 == mWavFilePtr->getFrameSize()) )
            {
                // TODO Copy data in two 32-bit buffers mCopiedDataL and mCopiedDataR
                LOG("24-bps stereo is not implemented yet" << std::endl);
                success = false;
                lame_close(mLameContext); mLameContext = NULL;
                continue;
            }
            else if( (32 == bps) || ((24 == bps) && (8 == mWavFilePtr->getFrameSize())) )
            {
#if 0  // This is available only in LAME 3.100
                encoded = lame_encode_buffer_interleaved_int(mLameContext,
                        (int *) mWavFilePtr->getRawAudioDataPtr(), numSamples,
                        mMp3Buffer, mp3bufsz);
#else
                // Allocate temp channel buffers
                uint32_t datasz = mWavFilePtr->getRawAudioDataSize();
                std::vector<uint8_t> copiedDataLVec;
                std::vector<uint8_t> copiedDataRVec;
                try {
                    copiedDataLVec.resize(datasz/2);
                    copiedDataRVec.resize(datasz/2);
                } catch(...) {
                    LOG("ERROR allocating copiedDataLVec or copiedDataRVec" << std::endl);
                    success = false;
                    lame_close(mLameContext); mLameContext = NULL;
                    break;
                }
                uint8_t* mCopiedDataL = &copiedDataLVec[0];
                uint8_t* mCopiedDataR = &copiedDataRVec[0];

                // Copy data in separate channel buffers
                int* lchan = (int *) mCopiedDataL;
                int* rchan = (int *) mCopiedDataR;
                int* ichan = (int *) mWavFilePtr->getRawAudioDataPtr();
                for( uint32_t i=0, l=0, r=0; i<datasz/sizeof(int); i++ )
                {
                    lchan[l++] = ichan[i];
                    rchan[r++] = ichan[++i];
                }

                encoded = lame_encode_buffer_int(mLameContext, (int *) mCopiedDataL,
                        (int *)mCopiedDataR, numSamples, mMp3Buffer, mp3bufsz);
#endif // LAME ver
            }
        }

        if( encoded <= 0 )
        {
            LOG("ERROR in lame_encode_buffer : " << encoded << std::endl);
            success = false;
        }
        else
        {
            // Create/open output mp3 file
            mMp3File.open(mMp3Uri.c_str(), std::ios::out | std::ios::trunc | std::ios::binary);
            if( ! mMp3File.is_open() )
            {
                LOG("ERROR opening mp3 file " << mMp3Uri << " for writing" << std::endl);
                success = false;
            }
            else
            {
                // Write mp3 buffer in the file
                mMp3File.write(reinterpret_cast<char*>(mMp3Buffer), encoded);
                if( !mMp3File )
                {
                    LOG("ERROR writing mp3 file " << mMp3Uri << std::endl);
                    success = false;
                }
                // Flush the buffer in the file
                int flushed = lame_encode_flush(mLameContext, mMp3Buffer, mp3bufsz);
                if( flushed > 0 )
                {
                    mMp3File.write(reinterpret_cast<char*>(mMp3Buffer), flushed);
                    if( !mMp3File )
                    {
                        LOG("ERROR writing flushed data to " << mMp3Uri << std::endl);
                        success = false;
                    }
                }
                else if( flushed < 0 )
                {
                    LOG("ERROR in lame_encode_flush : " << flushed << std::endl);
                    success = false;
                }
            }
        }

        if( mMp3File.is_open() )
        {
            mMp3File.close();
            if( mMp3File.fail() )
            {
                LOG("ERROR closing mp3 file " << mMp3Uri << std::endl);
                success = false;
            }
            mMp3File.clear();
        }
        lame_close(mLameContext); mLameContext = NULL;
        chunkNum++;
    }
    if( chunkNum == 0 || mWavFilePtr->hasError() ) success = false;
    LOG("Thread " << pthread_self() << " encoded " << chunkNum <<
            " wav chunk(s) from '" << mWavFilePtr->getURI() << "'" << std::endl);
    return success ? chunkNum : -1;
}
