# Runs GEMC using the gcard, on LUND generated events.


def C_runGemc(scard, **kwargs):

	gemcInputOptions = ""

	if scard.genExecutable == 'gemc':
		gemcInputOptions = scard.genOptions
	else:
		gemcInputOptions = """ -INPUT_GEN_FILE="lund, {0}" """.format(scard.genOutput)


	runGemc = """
# Run GEMC
# --------

# saving date for bookmarking purposes:
set gemcDate = `date`

# copying the gcard to gemc.gcard
cp /jlab/clas12Tags/$CLAS12TAG"/config/"{2}".gcard gemc.gcard"

echo
echo GEMC executable: `which gemc`
gemc -USE_GUI=0 -OUTPUT="evio, gemc.evio" -N={0} {1} gemc.gcard
echo
printf "GEMC Completed on: "; /bin/date
echo
echo "Directory Content After GEMC:"
ls -l
echo

# End of GEMC
# -----------

""".format(scard.nevents, gemcInputOptions, scard.configuration, clastag)

	return runGemc
