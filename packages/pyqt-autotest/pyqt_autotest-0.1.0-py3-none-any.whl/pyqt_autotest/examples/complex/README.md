To try this usage example, you will need to first install the package on the [transcriber repository](https://github.com/ewancook/transcriber).

This usage example can be executed from the command line as follows:

```sh
autotest -t pyqt_autotest.examples.complex.test.ComplexRandomTest -r 5 -a 10 -w 100
```

This test uncovered a QThread termination problem in the transcriber when closing the widget:

```sh
$ autotest -t pyqt_autotest.examples.complex.test.ComplexRandomTest -r 5 -a 10 -w 100
Running... (1/5): 100%|########################################################|
QThread: Destroyed while thread is still running
```