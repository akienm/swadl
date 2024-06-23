cd $SWADL_HOME$
cd Project/demos
del FAILURE_*.png
del test_*.log
nose2 google_unit_tests
