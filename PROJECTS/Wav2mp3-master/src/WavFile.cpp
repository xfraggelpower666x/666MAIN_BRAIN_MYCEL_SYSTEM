/******************************************************************************
 * @author Assen Kirov                                                        *
 ******************************************************************************/

#include <algorithm>
#include <cstring>
#include <limits>
#include "WavFile.h"
#include "Log.h"

using namespace wav2mp3;


WavFile::WavFile( const std::string& uri ):
        mFileUri(uri),
        mFile(uri.c_str(), std::ios::in | std::ios::binary),  // Opens the file
        mFileData(),
        mRiffHPtr(NULL),
        mFmtHPtr(NULL),
        mDataHPtr(NULL),
        mRiffEndOffset(0),
        mNextChunkOffset(0),
        mParseError(false)
{
}


WavFile::~WavFile()
{
    if( mFile.is_open() )
    {
        LOG("Closing wav file " << mFileUri << std::endl);
        mFile.close();
    }
}


int WavFile::readEntireFile()
{
    if( !mFileData.empty() ) return static_cast<int>(mFileData.size());  // Already read

    if( !mFile.is_open() )
    {
        mFile.clear();
        mFile.open(mFileUri.c_str(), std::ios::in | std::ios::binary);
    }

    if( mFile.is_open() )
    {
        mFile.seekg(0, std::ios::end);
        std::streamoff fileSize = mFile.tellg();
        if( fileSize <= 0 ||
            static_cast<unsigned long long>(fileSize) >
                static_cast<unsigned long long>(std::numeric_limits<int>::max()) )
        {
            mFile.close();
            return 0;
        }
        mFileData.resize(static_cast<size_t>(fileSize));
        mFile.seekg(0, std::ios::beg);
        mFile.read(&mFileData[0], static_cast<std::streamsize>(mFileData.size()));
        if( !mFile )
        {
            mFileData.clear();
            mFile.close();
            return 0;
        }
        mFile.close();
    }

    return static_cast<int>(mFileData.size());
}


bool WavFile::findNextWavChunk()
{
    if( mFileData.empty() )
    {
        this->readEntireFile();  // Try to fill mFileData
        if( mFileData.empty() )
        {
            LOG("Can't read file " << mFileUri << std::endl);
            mParseError = true;
            return false;  // If still empty - give up
        }
    }

    if( NULL == mRiffHPtr )
    {
        size_t riffOffset = 0;
        while( riffOffset + sizeof(RIFFHeader) <= mFileData.size() &&
               std::memcmp(&mFileData[riffOffset], "RIFF", 4) != 0 )
            ++riffOffset;

        if( riffOffset + sizeof(RIFFHeader) > mFileData.size() )
        {
            LOG("Can't find RIFF header in file " << mFileUri << std::endl);
            mFmtHPtr  = NULL;
            mDataHPtr = NULL;
            mParseError = true;
            return false;
        }

        RIFFHeader* riffhp = reinterpret_cast<RIFFHeader*>(&mFileData[riffOffset]);
        const uint64_t riffEnd = static_cast<uint64_t>(riffOffset) + 8 + riffhp->chunksz;
        if( std::memcmp(riffhp->format, "WAVE", 4) != 0 ||
            riffhp->chunksz < 4 || riffEnd > mFileData.size() )
        {
            LOG("Invalid or truncated RIFF/WAVE extent in file " << mFileUri << std::endl);
            mFmtHPtr = NULL;
            mDataHPtr = NULL;
            mParseError = true;
            return false;
        }
        mRiffHPtr = riffhp;
        mRiffEndOffset = static_cast<size_t>(riffEnd);
        mNextChunkOffset = riffOffset + sizeof(RIFFHeader);
    }

    mDataHPtr = NULL;
    while( mNextChunkOffset <= mRiffEndOffset &&
           mRiffEndOffset - mNextChunkOffset >= sizeof(DataHeader) )
    {
        const size_t chunkOffset = mNextChunkOffset;
        uint32_t chunkSize;
        std::memcpy(&chunkSize, &mFileData[chunkOffset + 4], sizeof(chunkSize));
        const uint64_t payloadEnd = static_cast<uint64_t>(chunkOffset) + 8 + chunkSize;
        const uint64_t paddedEnd = payloadEnd + (chunkSize & 1);
        if( payloadEnd > mRiffEndOffset || paddedEnd > mRiffEndOffset )
        {
            LOG("Invalid chunk extent in file " << mFileUri << std::endl);
            mFmtHPtr = NULL;
            mParseError = true;
            return false;
        }

        const char* chunkId = &mFileData[chunkOffset];
        if( std::memcmp(chunkId, "fmt ", 4) == 0 )
        {
            if( chunkSize < 16 )
            {
                LOG("Truncated fmt chunk in file " << mFileUri << std::endl);
                mFmtHPtr = NULL;
                mParseError = true;
                return false;
            }
            FMTHeader* fmthp = reinterpret_cast<FMTHeader*>(&mFileData[chunkOffset]);
            const uint16_t bps = fmthp->bitspersamp;
            if( fmthp->fmttag != 1 ||
                (fmthp->numchan != 1 && fmthp->numchan != 2) ||
                (bps != 8 && bps != 16 && bps != 24 && bps != 32) ||
                fmthp->blkalign != fmthp->numchan * (bps / 8) )
            {
                LOG("Unsupported PCM fmt chunk in file " << mFileUri << std::endl);
                mFmtHPtr = NULL;
                mParseError = true;
                return false;
            }
            mFmtHPtr = fmthp;
        }

        if( std::memcmp(chunkId, "data", 4) == 0 )
        {
            if( NULL == mFmtHPtr )
            {
                LOG("Data chunk precedes a supported fmt chunk in file " << mFileUri << std::endl);
                mParseError = true;
                return false;
            }
            if( chunkSize % mFmtHPtr->blkalign != 0 )
            {
                LOG("Misaligned data chunk in file " << mFileUri << std::endl);
                mParseError = true;
                return false;
            }
            mDataHPtr = reinterpret_cast<DataHeader*>(&mFileData[chunkOffset]);
            mNextChunkOffset = static_cast<size_t>(paddedEnd);
            return true;
        }

        mNextChunkOffset = static_cast<size_t>(paddedEnd);
    }

    if( mNextChunkOffset != mRiffEndOffset )
    {
        LOG("Truncated chunk header in file " << mFileUri << std::endl);
        mParseError = true;
        return false;
    }

    if( NULL == mFmtHPtr )
        LOG("Can't find a supported PCM fmt chunk in file " << mFileUri << std::endl);
    return false;
}


uint16_t WavFile::getNumChannels() const
{
    if( NULL != mFmtHPtr )
    {
        return mFmtHPtr->numchan;
    }
    else
    {
        return 0;
    }
}


uint32_t WavFile::getSampleRate() const
{
    if( NULL != mFmtHPtr )
    {
        return mFmtHPtr->samprate;
    }
    else
    {
        return 0;
    }
}


uint32_t WavFile::getByteRate() const
{
    if( NULL != mFmtHPtr )
    {
        return mFmtHPtr->byterate;
    }
    else
    {
        return 0;
    }
}


uint16_t WavFile::getFrameSize() const
{
    if( NULL != mFmtHPtr )
    {
        return mFmtHPtr->blkalign;
    }
    else
    {
        return 0;
    }
}


uint16_t WavFile::getBitsPerSample() const
{
    if( NULL != mFmtHPtr )
    {
        return mFmtHPtr->bitspersamp;
    }
    else
    {
        return 0;
    }
}


const char* WavFile::getRawAudioDataPtr() const
{
    if( NULL != mDataHPtr )
    {
        return (reinterpret_cast<char*>(mDataHPtr) + sizeof(DataHeader));
    }
    else
    {
        return NULL;
    }
}


/*
 * @return the smaller of: data size in the header and the remaining file size
 */
uint32_t WavFile::getRawAudioDataSize() const
{
    if( NULL != mDataHPtr )
    {
        return mDataHPtr->datasz;
    }
    else
    {
        return 0;
    }
}
