all: libmodel.so
libmodel.so: iso_c_utils.f90 model.f90
	gfortran -g iso_c_utils.f90 model.f90 -fPIC -shared -o libmodel.so
