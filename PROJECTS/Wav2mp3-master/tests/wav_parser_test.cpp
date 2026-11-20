#include <pthread.h>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "WavFile.h"

pthread_mutex_t gLogMutex = PTHREAD_MUTEX_INITIALIZER;

namespace {

void append16(std::vector<char>& data, unsigned int value)
{
    data.push_back(static_cast<char>(value & 0xff));
    data.push_back(static_cast<char>((value >> 8) & 0xff));
}

void append32(std::vector<char>& data, unsigned int value)
{
    data.push_back(static_cast<char>(value & 0xff));
    data.push_back(static_cast<char>((value >> 8) & 0xff));
    data.push_back(static_cast<char>((value >> 16) & 0xff));
    data.push_back(static_cast<char>((value >> 24) & 0xff));
}

void patch32(std::vector<char>& data, size_t offset, unsigned int value)
{
    for( size_t i=0; i<4; ++i )
        data[offset+i] = static_cast<char>((value >> (i*8)) & 0xff);
}

std::vector<char> makeWav(const std::vector<char>& sampleData)
{
    std::vector<char> body;
    body.insert(body.end(), "WAVE", "WAVE" + 4);
    body.insert(body.end(), "fmt ", "fmt " + 4);
    append32(body, 16);
    append16(body, 1);
    append16(body, 1);
    append32(body, 8000);
    append32(body, 16000);
    append16(body, 2);
    append16(body, 16);
    body.insert(body.end(), "data", "data" + 4);
    append32(body, static_cast<unsigned int>(sampleData.size()));
    body.insert(body.end(), sampleData.begin(), sampleData.end());
    if( sampleData.size() & 1 ) body.push_back(0);

    std::vector<char> wav;
    wav.insert(wav.end(), "RIFF", "RIFF" + 4);
    append32(wav, static_cast<unsigned int>(body.size()));
    wav.insert(wav.end(), body.begin(), body.end());
    return wav;
}

void writeFile(const std::string& path, const std::vector<char>& data)
{
    std::ofstream file(path.c_str(), std::ios::binary | std::ios::trunc);
    if( !file.is_open() )
    {
        std::cerr << "Could not create parser fixture " << path << std::endl;
        std::exit(1);
    }
    file.write(&data[0], static_cast<std::streamsize>(data.size()));
    if( !file )
    {
        std::cerr << "Could not write parser fixture " << path << std::endl;
        std::exit(1);
    }
}

void require(bool condition, const char* message)
{
    if( !condition )
    {
        std::cerr << message << std::endl;
        std::exit(1);
    }
}

void requireRejected(const std::string& path, const std::vector<char>& data,
                     const char* message)
{
    writeFile(path, data);
    wav2mp3::WavFile wav(path);
    require(wav.readEntireFile() > 0, "Could not read parser fixture");
    require(!wav.findNextWavChunk(), message);
    require(wav.hasError(), "Malformed WAV did not set the parse error");
    std::remove(path.c_str());
}

} // namespace

int main(int argc, char* argv[])
{
    if( argc != 2 )
    {
        std::cerr << "Usage: wav_parser_test temporary_directory" << std::endl;
        return 2;
    }

    const std::string base = std::string(argv[1]) + "/wav2mp3-parser-test-";
    std::vector<char> valid = makeWav(std::vector<char>(2, 0));
    const std::string validPath = base + "valid.wav";
    writeFile(validPath, valid);
    {
        wav2mp3::WavFile wav(validPath);
        require(wav.readEntireFile() == static_cast<int>(valid.size()),
                "Could not read valid WAV");
        require(wav.findNextWavChunk(), "Valid PCM WAV was rejected");
        require(wav.getNumChannels() == 1 && wav.getBitsPerSample() == 16 &&
                wav.getRawAudioDataSize() == 2, "Valid WAV metadata was parsed incorrectly");
    }
    std::remove(validPath.c_str());

    std::vector<char> truncated = valid;
    patch32(truncated, 4, static_cast<unsigned int>(truncated.size()));
    requireRejected(base + "truncated.wav", truncated,
                    "RIFF extent beyond EOF was accepted");

    std::vector<char> oversizedChunk = valid;
    patch32(oversizedChunk, 40, 0xffffffffu);
    requireRejected(base + "chunk.wav", oversizedChunk,
                    "Chunk payload beyond RIFF extent was accepted");

    std::vector<char> misaligned = makeWav(std::vector<char>(1, 0));
    requireRejected(base + "misaligned.wav", misaligned,
                    "PCM data not aligned to a complete frame was accepted");

    std::cout << "WAV parser bounds and frame-alignment tests passed" << std::endl;
    return 0;
}
