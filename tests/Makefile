all: libmodel.so
libmodel.so:
	gfortran -g iso_c_utils.f90 model.f90 -fPIC -shared -o libmodel.so
