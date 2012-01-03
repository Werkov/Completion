#ifndef FRACTION_H
#define FRACTION_H

namespace num {
    typedef double value_type;

    class Fraction {
    public:
        Fraction();
        Fraction(int a, int b);
        Fraction add(Fraction b);
        Fraction reduce();
        value_type val();
        int a, b;

    };
};
#endif