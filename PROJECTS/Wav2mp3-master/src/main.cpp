/******************************************************************************
 * @author Assen Kirov                                                        *
 ******************************************************************************/

#ifdef USE_CPP11_THREADS
 #include <thread>
#else  // POSIX
 #include <pthread.h>
#endif  // USE_CPP11_THREADS

#if defined(__GXX_EXPERIMENTAL_CXX0X) || __cplusplus >= 201103L
 #include <memory>
 using std::shared_ptr;
#else  // TR1
 #include <tr1/memory>
 using std::tr1::shared_ptr;
#endif  // c++11

#ifdef _WIN32
 #include <windows.h>
#else  // POSIX
 #include <unistd.h>
#endif  // _WIN32

#include <vector>
#include <string>
#include <climits>
#include <cstring>
#include <stdexcept>
#include <dirent.h>

#include "SyncQueue.h"
#include "WavFile.h"
#include "Encoder.h"
#include "Log.h"

using namespace wav2mp3;


namespace {

/**
 * Use a global variable to track the number of remaining files to be processed.
 * (Re)Initialize it in the manager thread with total number of wav files.
 * Decrease it after a file is encoded. When it becomes 0 all files are processed.
 * Signal this with a condition variable.
 * We can set it to 0 manually to flag a stop request.
 */
int             gNFilesToProcess = INT_MAX;
bool            gProcessingFailed = false;
pthread_cond_t  gNFilesCVar;
pthread_mutex_t gNFilesMutex;

void setNFilesToProcess(int count)
{
    pthread_mutex_lock(&gNFilesMutex);
    gNFilesToProcess = count;
    if( count <= 0 ) pthread_cond_signal(&gNFilesCVar);
    pthread_mutex_unlock(&gNFilesMutex);
}


void decNFilesToProcess()
{
    pthread_mutex_lock(&gNFilesMutex);
    if( gNFilesToProcess > 0 && --gNFilesToProcess == 0 )
        pthread_cond_signal(&gNFilesCVar);
    pthread_mutex_unlock(&gNFilesMutex);
}

void markProcessingFailed()
{
    pthread_mutex_lock(&gNFilesMutex);
    gProcessingFailed = true;
    pthread_mutex_unlock(&gNFilesMutex);
}


int getNFilesToProcess()
{
    Locker lock(gNFilesMutex);
    return gNFilesToProcess;
}


std::vector<std::string> gWavFileURIs;

} // anonymous namespace


pthread_mutex_t gLogMutex;  // TODO put it in wav2mp3 namespace


void* work_manager(void* arg)
{
    // Get the work queue pointer
    SyncQueue< shared_ptr<WavFile> >* wavFileQueue =
                                  (SyncQueue< shared_ptr<WavFile> >*) arg;
    if( NULL == wavFileQueue ) pthread_exit((void*) 0);  // Signal CV before exit?

    if( gWavFileURIs.size() > static_cast<size_t>(INT_MAX) )
    {
        LOG("Too many WAV files to process" << std::endl);
        markProcessingFailed();
        setNFilesToProcess(0);
        return NULL;
    }
    int numWavFiles = static_cast<int>(gWavFileURIs.size());

    setNFilesToProcess(numWavFiles);

    // Enqueue wav files in the work queue until the list is empty (or stop is requested)
    int i=0;
    for( ; i<numWavFiles && getNFilesToProcess()>0; i++ )
    {
        shared_ptr<WavFile> wavFile;
        std::string uri = gWavFileURIs[i];
        try {
            wavFile.reset(new WavFile(uri));  // Will be freed automatically
            if( wavFile->readEntireFile() == 0 )
                throw std::runtime_error("unable to read WAV file");
        } catch(...) {
            LOG("Error opening wav file " << uri << std::endl);
            markProcessingFailed();
            decNFilesToProcess();
            continue;
        }
        try {
            wavFileQueue->enqueue(wavFile);
        } catch(const std::exception& error) {
            LOG("Error queueing wav file " << uri << ": " << error.what() << std::endl);
            markProcessingFailed();
            decNFilesToProcess();
        } catch(...) {
            LOG("Unknown error queueing wav file " << uri << std::endl);
            markProcessingFailed();
            decNFilesToProcess();
        }
    }
    LOG("Work manager is done" << std::endl);

    return NULL;
}


void* worker(void* arg)
{
    // Get the work queue pointer
    SyncQueue< shared_ptr<WavFile> >* wavFileQueue =
                                  (SyncQueue< shared_ptr<WavFile> >*) arg;
    if( NULL == wavFileQueue ) pthread_exit((void*) 0);

    unsigned int numProcFiles=0;  // Number of files processed by this thread

    while( true )
    {
        // Dequeue wav file from work queue and encode it. Block if the queue is empty
        shared_ptr<WavFile> wavFile;
        try {
            wavFile = wavFileQueue->dequeue();
        } catch(const std::exception& error) {
            LOG("Error dequeuing wav file: " << error.what() << std::endl);
            markProcessingFailed();
            setNFilesToProcess(0);
            break;
        } catch(...) {
            LOG("Unknown error dequeuing wav file" << std::endl);
            markProcessingFailed();
            setNFilesToProcess(0);
            break;
        }

        if( wavFile )
        {
            // Encode wav file
            try {
                Encoder encoder(wavFile);
                if( encoder.encode() < 0 )
                    markProcessingFailed();
            } catch(const std::exception& error) {
                LOG("Error encoding wav file " << wavFile->getURI() << ": " <<
                    error.what() << std::endl);
                markProcessingFailed();
            } catch(...) {
                LOG("Unknown error encoding wav file " << wavFile->getURI() << std::endl);
                markProcessingFailed();
            }

            numProcFiles++;
        }  // Resources will be freed here
        else
        {
            LOG("Received empty work item from queue" << std::endl);
            markProcessingFailed();
            decNFilesToProcess();
            continue;
        }

        decNFilesToProcess();
    }

    pthread_exit((void*) numProcFiles);
}


int main(int argc, char* argv[])
{
    // Parse arguments and set gWavFileURIs
    if( argc < 2 )
    {
        std::cerr << "Usage: " << argv[0] << " wav_folder_uri" << std::endl;
        return 1;
    }

    // Fill the list of wav file URIs
    std::string wavFolder(argv[1]);
    size_t len = wavFolder.length();
    if( len == 0 )
    {
        std::cerr << "Folder URI cannot be empty" << std::endl;
        return 1;
    }
    if( wavFolder[len-1] != '/' && wavFolder[len-1] != '\\' )
        wavFolder += "/";
    DIR* dir;
    if( (dir = opendir (wavFolder.c_str())) == NULL )
    {
        std::cerr << "Error opening folder '" << wavFolder << "'" << std::endl;
        return 1;
    }
    struct dirent* dent;
    while( (dent = readdir (dir)) != NULL )
    {
        const char* fname = dent->d_name;
        if( !strcmp(".", fname) || !strcmp("..", fname) ) continue;
        len = strlen(fname);
        if( (len > 4) && (!strcasecmp(".wav", fname+len-4)) )
            gWavFileURIs.push_back(wavFolder + std::string(fname));
    }
    closedir (dir);
    if( 0 == gWavFileURIs.size() )
    {
        std::cerr << "There are no wav files in '" << wavFolder << "' folder" << std::endl;
        return 1;
    }

    // Initialize global condition variable and mutexes
    pthread_mutex_init(&gLogMutex, NULL);
    pthread_mutex_init(&gNFilesMutex, NULL);
    pthread_cond_init(&gNFilesCVar, NULL);

    // TODO Add signal handler for CTRL+C to set gNFilesToProcess=0 and signal gNFilesCVar

    // Get the number of CPU cores
    long numCores;
#ifdef USE_CPP11_THREADS
    numCores = std::thread::hardware_concurrency();
#elif defined(_WIN32)
    SYSTEM_INFO sysinfo;
    GetSystemInfo(&sysinfo);
    numCores = sysinfo.dwNumberOfProcessors;
#else  // POSIX
    numCores = sysconf(_SC_NPROCESSORS_ONLN);
#endif
    if( numCores < 1 ) numCores = 1;
    LOG("Number of CPU cores: " << numCores << std::endl);

    // Create work queue for wav files.
#if defined(__GXX_EXPERIMENTAL_CXX0X) || __cplusplus >= 201103L
    std::unique_ptr<SyncQueue<shared_ptr<WavFile> > >
        wavFileQueuePtr(new SyncQueue<shared_ptr<WavFile> >(2*numCores));
#else
    std::auto_ptr<SyncQueue<shared_ptr<WavFile> > >
        wavFileQueuePtr(new SyncQueue<shared_ptr<WavFile> >(2*numCores));
#endif  // c++11

    // Create pool of encoding threads (workers) and point them to the work queue
    std::vector<pthread_t> encoderThreads;
    encoderThreads.reserve(static_cast<size_t>(numCores));
    for( int i=0; i<numCores; i++ )
    {
        pthread_t thread;
        int rc = pthread_create(&thread, 0, worker, wavFileQueuePtr.get());
        if( rc != 0 )
        {
            LOG("Error creating encoder thread: " << strerror(rc) << std::endl);
            markProcessingFailed();
            continue;
        }
        encoderThreads.push_back(thread);
    }

    if( encoderThreads.empty() )
    {
        LOG("No encoder threads could be started" << std::endl);
        setNFilesToProcess(0);
    }

    bool managerStarted = false;
    pthread_t managerThread;
    if( !encoderThreads.empty() )
    {
        int rc = pthread_create(&managerThread, 0, work_manager, wavFileQueuePtr.get());
        if( rc != 0 )
        {
            LOG("Error creating work manager thread: " << strerror(rc) << std::endl);
            markProcessingFailed();
            setNFilesToProcess(0);
        }
        else
            managerStarted = true;
    }

    if( managerStarted )
    {
        pthread_mutex_lock(&gNFilesMutex);
        while( gNFilesToProcess > 0 )
            pthread_cond_wait(&gNFilesCVar, &gNFilesMutex);
        pthread_mutex_unlock(&gNFilesMutex);
        LOG("Work end signaled" << std::endl);
        pthread_join(managerThread, NULL);
        LOG("Work manager joined" << std::endl);
    }

    // Cancel and join only threads that were successfully created.
    for( size_t i=0; i<encoderThreads.size(); i++ )
        pthread_cancel(encoderThreads[i]);
    for( size_t i=0; i<encoderThreads.size(); i++ )
        pthread_join(encoderThreads[i], NULL);
    LOG("Workers joined" << std::endl);

    pthread_mutex_lock(&gNFilesMutex);
    bool processingFailed = gProcessingFailed;
    pthread_mutex_unlock(&gNFilesMutex);

    // Destroy work queue and globals
    wavFileQueuePtr.reset();

    pthread_cond_destroy(&gNFilesCVar);
    pthread_mutex_destroy(&gNFilesMutex);
    pthread_mutex_destroy(&gLogMutex);  // Logs in destructors may crash. Leave this to the OS. Or don't use logs in destructors. Or destroy objects before tis point.

    return processingFailed ? 1 : 0;
}
