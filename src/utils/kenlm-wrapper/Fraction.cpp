#include "Fraction.h"

static int gcd(int a, int b);

num::Fraction::Fraction() : a(0), b(1) {
}

num::Fraction::Fraction(int a, int b) : a(a), b(b) {
}

num::Fraction num::Fraction::add(num::Fraction b) {
    return num::Fraction(this->a * b.b + b.a * this->a, this->b * b.b);
}
num::Fraction num::Fraction::reduce() {
    int g = gcd(this->a, this->b);
    return num::Fraction(this->a / g, this->b / g);
}
num::value_type num::Fraction::val() {
    return (double)this->a / this->b;
}

int gcd(int a, int b) {
    int r = a % b;
    while(r > 0){
        a = b;
        b = r;
        r = a % b;
    }
    return b;
}

