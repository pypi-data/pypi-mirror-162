To try this usage example, you will need to first install the package on the [N-Body-Simulations github repository](https://github.com/robertapplin/N-Body-Simulations).

This usage example can be executed from the command line as follows:

```sh
autotest -t pyqt_autotest.examples.moderate.test.ModerateRandomTest -r 5 -a 10 -w 300
```

This test uncovered a previously unknown issue where closing the main widget would leave behind some widgets:

```sh
$ autotest -t pyqt_autotest.examples.moderate.test.ModerateRandomTest -r 5 -a 10 -w 300
Running... (1/5): 100%|########################################################|
An exception occurred, please correct the following:

    Unexpected top level widget(s) detected after closing your widget:
    ['QWidget', 'QWidget', 'QWidget', 'QWidget', 'QWidget', 'QWidget', 'QWidget']
```
