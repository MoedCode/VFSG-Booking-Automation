#include <iostream>
using namespace std;

int func(int &x) {
    x = x + 5;
    return x;
}

int main() {
    int a = 3;
    cout << func(a) << " " << a;
}