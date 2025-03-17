#include <assert.h>
#include <iostream>
using namespace std;

int add(int a, int b) {
    return a + b;
}

void test_add() {
    assert(add(1, 2) == 3);
    assert(add(-1, -1) == -2);
    assert(add(0, 0) == 0);
    assert(add(100, 200) == 300);
    assert(add(-100, 100) == 0);
}

int main() {
    test_add();
    cout << "All tests passed!" << endl;
    return 0;
}
