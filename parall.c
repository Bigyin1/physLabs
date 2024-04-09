
#include <math.h>
#include <stdint.h>
#include <stdio.h>

double function(double x) { return exp(-x * x); }

int main() {

  double left = 0.0000;
  double right = 1;

  double delta = (right - left) / 1000000;
  // printf("%lf\n", delta);

  double integral = 0;

  for (size_t i = 0; i < 1000000; i++) {

    double yl = function(left + i * delta);
    double yr = function(left + (i + 1) * delta);
    // printf("%lf %lf\n", yl, yr);

    integral += 0.50 * (yl + yr) * delta;
  }

  printf("%.10lf\n", integral);
}
