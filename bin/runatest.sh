cls
echo "runatest.sh called with $1 $2 $3 $4 $5 $6 $7 $8 $9"
echo "2024 Akien Maciain"
echo "Purpose: To clean up from the last run, and display output files"
echo "Usage:"
echo "   Runs under bash"
echo "   Run with: bash ./runatest.sh [1] [2] [3]"
echo "       [1] = runner (nose2 or pytest or whatever)"
echo "       [2] = script name in whatever form the specified test runner wants"
echo "             nose2 prefers without the .py"
echo "             pytest preferw with the .py"
echo "       [3] whatever other arguments"
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
if [ -d "FAILURE_*.png" ] ; then
    rm FAILURE_*.png
fi
if [ -d "test_*.log" ] ; then
    rm test_*.log
fi
echo "Calling: $1 $2 $3 $4 $5 $6 $7 $8 $9"
$1 $2 $3 $4 $5 $6 $7 $8 $9
if [ -d "test_failures.log" ] ; then
    echo "test_failures.log:"
    cat test_failures.log
    echo ""
fi
echo "For all test results: cat test_results.log"
