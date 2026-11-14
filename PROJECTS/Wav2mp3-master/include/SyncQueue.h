/******************************************************************************
 * @author Assen Kirov                                                        *
 ******************************************************************************/

#ifndef __SYNCQUEUE_H__
#define __SYNCQUEUE_H__

#include <pthread.h>
#include <semaphore.h>
#include <assert.h>
#include <deque>
#include <climits>
#include <cerrno>
#include <stdexcept>
#include "Locker.h"

namespace wav2mp3 {


template <typename T>
class SyncQueue
{
  public:
    SyncQueue( unsigned int maxElements=INT_MAX );
    ~SyncQueue();

    void enqueue( const T& item );
    T dequeue();
    size_t getSize() const;

  private:
    /// Disable copying
    SyncQueue(const SyncQueue& other);
    SyncQueue& operator=(const SyncQueue& other);

    /// The actual queue
    std::deque<T> mQueue;

    /**
     *  We need two semaphores: one counting the number of empty slots and the
     *  other counting the number of occupied slots.
     *  We also need a mutex to protect against race conditions.
     */
    sem_t mSemEmpty;
    sem_t mSemFull;
    mutable pthread_mutex_t mMutex;
};


template <typename T>
SyncQueue<T>::SyncQueue( unsigned int maxElements ):
        mQueue()
{
    sem_init(&mSemEmpty, 0, maxElements);
    sem_init(&mSemFull, 0, 0);
    pthread_mutex_init(&mMutex, NULL);
}


template <typename T>
SyncQueue<T>::~SyncQueue()
{
    // We MUST NOT try to use the queue any more
    sem_destroy(&mSemEmpty);
    sem_destroy(&mSemFull);
    pthread_mutex_destroy(&mMutex);
}


template <typename T>
void SyncQueue<T>::enqueue( const T& item )
{
    while( sem_wait(&mSemEmpty) != 0 )
    {
        if( errno == EINTR ) continue;
        throw std::runtime_error("sem_wait failed while enqueueing");
    }

    try {
        Locker lock(mMutex);
        mQueue.push_back(item);
    } catch(...) {
        sem_post(&mSemEmpty);
        throw;
    }

    if( sem_post(&mSemFull) != 0 )
        throw std::runtime_error("sem_post failed after enqueue");
}


template <typename T>
T SyncQueue<T>::dequeue()
{
    while( sem_wait(&mSemFull) != 0 )
    {
        if( errno == EINTR ) continue;
        throw std::runtime_error("sem_wait failed while dequeueing");
    }

    try {
        Locker lock(mMutex);
        assert(mQueue.size() > 0);
        T item = mQueue.front();
        mQueue.pop_front();
        if( sem_post(&mSemEmpty) != 0 )
            throw std::runtime_error("sem_post failed after dequeue");
        return item;
    } catch(...) {
        sem_post(&mSemFull);
        throw;
    }

}


template <typename T>
size_t SyncQueue<T>::getSize() const
{
    Locker lock(mMutex);
    return mQueue.size();
}


} // namespace

#endif // __SYNCQUEUE_H__
