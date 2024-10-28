from libcpp cimport bool


cdef extern from "linked_list.h":
    struct sLinkedList:
        void* data
        sLinkedList* next
    
    ctypedef sLinkedList* LinkedList
    
    LinkedList LinkedList_create()
    
    void LinkedList_destroy(LinkedList self)
    
    ctypedef void (*LinkedListValueDeleteFunction) (void*)
    
    void LinkedList_destroyDeep(LinkedList self, LinkedListValueDeleteFunction valueDeleteFunction)
    
    void LinkedList_destroyStatic(LinkedList self)
    
    void LinkedList_add(LinkedList self, void* data)
    
    bool LinkedList_contains(LinkedList self, void* data)
    
    bool LinkedList_remove(LinkedList self, void* data)
    
    LinkedList LinkedList_get(LinkedList self, int index)
    
    LinkedList LinkedList_getNext(LinkedList self)
    
    LinkedList LinkedList_getLastElement(LinkedList self)
    
    LinkedList LinkedList_insertAfter(LinkedList listElement, void* data)
    
    int LinkedList_size(LinkedList self)
    
    void* LinkedList_getData(LinkedList self)
    
    void LinkedList_printStringList(LinkedList self)
