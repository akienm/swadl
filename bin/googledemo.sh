echo "googledemo.sh called with $1 $2 $3 $4 $5 $6 $7 $8 $9"
echo "2024 Akien Maciain"
echo "Purpose: To run the google_unit_tests demo in linux"
echo "placeholder script for now"
if [ ":$SWADL_HOME" = ":" ] ; then
    echo "So sad."
    echo "Friendly person, I cant do this without the"
    echo "SWADL_HOME environment variable being set first"
    echo "Please google mac bash profile file name"
    echo "and try your call again. this is a recoding."
    echo ""
else
    cd $SWADL_HOME$/Project/demos
    bash $SWADL_HOME/bin/runatest.sh nose2 google_unit_tests $1 $2 $3 $4 $5 $6 $7 $8 $9
fi



