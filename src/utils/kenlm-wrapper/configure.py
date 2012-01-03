import os.path
import os
import sipconfig

# The name of the SIP build file generated by SIP and used by the build
# system.
build_file = "config.sbf"

# Get the SIP configuration information.
config = sipconfig.Configuration()

# Run SIP to generate the code.
os.system(" ".join([config.sip_bin, "-c", ".", "-b", build_file, "kenlm-wrapper.sip"]))

# Create the Makefile.
# Installation path is within the project, not central (DEST_DIR won't work correctly)
makefile = sipconfig.SIPModuleMakefile(config, build_file, install_dir=os.path.abspath(".."), makefile="Makefile.generated")

# Add the library we are wrapping.  The name doesn't include any platform
# specific prefixes or extensions (e.g. the "lib" prefix on UNIX, or the
# ".dll" extension on Windows).
makefile.extra_libs = ["z"]

extra_bin_dirs = [os.path.abspath("../../../libs/kenlm/bin/lm"), os.path.abspath("../../../libs/kenlm/bin/util")]

# makefile.extra_lflags = [" ".join([os.path.join(bin, "*.o") for bin in extra_bin_dirs])] # unnecessary, included in kenlm-wrapper.o
makefile.extra_include_dirs = [os.path.abspath("../../../libs/kenlm")]
makefile.extra_lflags = ["Fraction.o", "kenlm-wrapper.o", "`pkg-config --libs --cflags icu-uc icu-io`"]
makefile.extra_defines = ["HAVE_ICU"]

# Generate the Makefile itself.
makefile.generate()