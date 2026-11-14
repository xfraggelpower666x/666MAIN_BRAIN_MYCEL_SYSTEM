#include <pthread.h>
#include <iostream>

#include "SyncQueue.h"

struct ConsumerArgs
{
    wav2mp3::SyncQueue<int>* queue;
    int value;
};

namespace {

void* consume(void* rawArgs)
{
    ConsumerArgs* args = static_cast<ConsumerArgs*>(rawArgs);
    args->value = args->queue->dequeue();
    return NULL;
}

bool runConsumers(wav2mp3::SyncQueue<int>& queue, ConsumerArgs* args,
                  unsigned int count)
{
    pthread_t threads[2];
    unsigned int started = 0;
    for( ; started<count; started++ )
    {
        args[started].queue = &queue;
        args[started].value = -1;
        if( pthread_create(&threads[started], NULL, consume, &args[started]) != 0 )
            break;
    }

    queue.close(started);

    bool success = started == count;
    for( unsigned int i=0; i<started; i++ )
    {
        if( pthread_join(threads[i], NULL) != 0 )
            success = false;
    }
    return success;
}

} // namespace

int main()
{
    ConsumerArgs results[2];
    wav2mp3::SyncQueue<int> queue(2);
    queue.enqueue(42);
    if( !runConsumers(queue, results, 2) ||
        !((results[0].value == 42 && results[1].value == 0) ||
          (results[0].value == 0 && results[1].value == 42)) )
    {
        std::cerr << "Queue did not drain before stopping consumers" << std::endl;
        return 1;
    }

    wav2mp3::SyncQueue<int> emptyQueue(2);
    if( !runConsumers(emptyQueue, results, 2) ||
        results[0].value != 0 || results[1].value != 0 )
    {
        std::cerr << "Closing an empty queue did not wake all consumers" << std::endl;
        return 1;
    }

    std::cout << "Queue shutdown tests passed" << std::endl;
    return 0;
}
