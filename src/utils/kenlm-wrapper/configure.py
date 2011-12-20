import os.path
import os
import sipconfig

# The name of the SIP build file generated by SIP and used by the build
# system.
build_file = "config.sbf"

kenlm_bin = [os.path.abspath("../../../libs/kenlm/bin/lm"), os.path.abspath("../../../libs/kenlm/bin/util")]
kenlm_src = [os.path.abspath("../../../libs/kenlm")]

# Get the SIP configuration information.
config = sipconfig.Configuration()

# Run SIP to generate the code.
os.system(" ".join([config.sip_bin, "-c", ".", "-b", build_file, "kenlm-wrapper.sip"]))

# Create the Makefile.
# Installation path is within the project, not central (DEST_DIR won't work correctly)
makefile = sipconfig.SIPModuleMakefile(config, build_file, install_dir=os.path.abspath(".."))

# Add the library we are wrapping.  The name doesn't include any platform
# specific prefixes or extensions (e.g. the "lib" prefix on UNIX, or the
# ".dll" extension on Windows).
makefile.extra_libs = ["z"]

makefile.extra_lflags = [" ".join([os.path.join(bin, "*.o") for bin in kenlm_bin])]
makefile.extra_include_dirs = kenlm_src

# Generate the Makefile itself.
makefile.generate()