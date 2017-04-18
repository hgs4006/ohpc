#----------------------------------------------------------------------------bh-
# This RPM .spec file is part of the OpenHPC project.
#
# It may have been modified from the default version supplied by the underlying
# release package (if available) in order to apply patches, perform customized
# build/install configurations, and supply additional files to support
# desired integration conventions.
#
#----------------------------------------------------------------------------eh-

# ptscotch - a parallel version of Graph, mesh and hypergraph partitioning library

#-ohpc-header-comp-begin----------------------------------------------

%include %{_sourcedir}/OHPC_macros
%{!?PROJ_DELIM: %global PROJ_DELIM -ohpc}

# OpenHPC convention: the default assumes the gnu compiler family;
# however, this can be overridden by specifing the compiler_family
# variable via rpmbuild or other mechanisms.

%{!?compiler_family: %global compiler_family gnu}

# Lmod dependency (note that lmod is pre-populated in the OpenHPC OBS build
# environment; if building outside, lmod remains a formal build dependency).
%if !0%{?OHPC_BUILD}
BuildRequires: lmod%{PROJ_DELIM}
%endif
# Compiler dependencies
%if %{compiler_family} == gnu
BuildRequires: gnu-compilers%{PROJ_DELIM}
Requires:      gnu-compilers%{PROJ_DELIM}
%endif
%if %{compiler_family} == intel
BuildRequires: intel-compilers-devel%{PROJ_DELIM}
Requires:      intel-compilers-devel%{PROJ_DELIM}
%if 0%{OHPC_BUILD}
BuildRequires: intel_licenses
%endif
%endif

# MPI dependencies
%{!?mpi_family:      %global mpi_family openmpi}

%if %{mpi_family} == impi
BuildRequires: intel-mpi-devel%{PROJ_DELIM}
Requires:      intel-mpi-devel%{PROJ_DELIM}
%endif
%if %{mpi_family} == mvapich2
BuildRequires: mvapich2-%{compiler_family}%{PROJ_DELIM}
Requires:      mvapich2-%{compiler_family}%{PROJ_DELIM}
%endif
%if %{mpi_family} == openmpi
BuildRequires: openmpi-%{compiler_family}%{PROJ_DELIM}
Requires:      openmpi-%{compiler_family}%{PROJ_DELIM}
%endif
%if %{mpi_family} == mpich
BuildRequires: mpich-%{compiler_family}%{PROJ_DELIM}
Requires:      mpich-%{compiler_family}%{PROJ_DELIM}
%endif

#-ohpc-header-comp-end------------------------------------------------

# Base package name
%define base_pname scotch
%define pname pt%{base_pname}
%define PNAME %(echo %{pname} | tr [a-z] [A-Z])

Name:	%{pname}-%{compiler_family}-%{mpi_family}%{PROJ_DELIM}
Version: 6.0.4
Release: 1
Summary: Graph, mesh and hypergraph partitioning library using MPI
License: CeCILL-C
Group: %{PROJ_NAME}/parallel-libs
URL: http://www.labri.fr/perso/pelegrin/scotch/
Source0: http://gforge.inria.fr/frs/download.php/file/34618/%{base_pname}_%{version}.tar.gz
Source1: scotch-Makefile.inc.in
Source2: scotch-rpmlintrc
Source3: OHPC_macros
Source4: OHPC_setup_compiler
Source5: OHPC_setup_mpi
Patch0:  scotch-%{version}-destdir.patch
BuildRoot: %{_tmppath}/%{pname}-%{version}-%{release}-root
DocDir:    %{OHPC_PUB}/doc/contrib

BuildRequires:	flex bison
%if 0%{?suse_version} >= 1100
BuildRequires:  libbz2-devel
BuildRequires:  zlib-devel
%else
%if 0%{?sles_version} || 0%{?suse_version}
BuildRequires:  bzip2
BuildRequires:  zlib-devel
%else
BuildRequires:  bzip2-devel
BuildRequires:  zlib-devel
%endif
%endif

# Requires:	

#Disable debug packages
%define debug_package %{nil}

# Default library install path
%define install_path %{OHPC_LIBS}/%{compiler_family}/%{mpi_family}/%{pname}/%{version}


%define _mpi_load					\
	export OHPC_COMPILER_FAMILY=%{compiler_family}; \
	export OHPC_MPI_FAMILY=%{mpi_family};		\
	. %{_sourcedir}/OHPC_setup_compiler;		\
	. %{_sourcedir}/OHPC_setup_mpi;					

%define _mpi_unload \
	module unload ${OHPC_MPI_FAMILY};


%description
Scotch is a software package for graph and mesh/hypergraph partitioning and
sparse matrix ordering.

%prep
%setup -c -q -n %{base_pname}_%{version}
pushd %{base_pname}_%{version}
%patch0 -p1
sed s/@RPMFLAGS@/'%{optflags} -fPIC'/ < %SOURCE1 > src/Makefile.inc
popd

%build
# OpenHPC compiler/mpi designation
. /etc/profile.d/lmod.sh
export OHPC_COMPILER_FAMILY=%{compiler_family}
export OHPC_MPI_FAMILY=%{mpi_family}
. %{_sourcedir}/OHPC_setup_compiler
. %{_sourcedir}/OHPC_setup_mpi

%define dobuild() \
make %{?_smp_mflags} %{pname}; \
mpicc -shared -Wl,-soname=lib%{pname}err.so.0 -o ../lib/lib%{pname}err.so.0.0 libscotch/library_error.o; \
mpicc -shared -Wl,-soname=lib%{pname}errexit.so.0 -o ../lib/lib%{pname}errexit.so.0.0  libscotch/library_error_exit.o; \
rm -f libscotch/library_error*.o; \
mpicc -shared -Wl,-soname=lib%{pname}.so.0 -o ../lib/lib%{pname}.so.0.0	libscotch/*.o ../lib/lib%{pname}err.so.0.0 -lgfortran -lz -lbz2 ; \
mpicc -shared -Wl,-soname=lib%{pname}parmetis.so.0 -o ../lib/lib%{pname}parmetis.so.0.0 libscotchmetis/*.o ../lib/lib%{pname}.so.0.0 ../lib/lib%{pname}err.so.0.0

pushd %{base_pname}_%{version}/src
%{_mpi_load}
%dobuild
%{_mpi_unload}
popd

%install
rm -rf ${RPM_BUILD_ROOT}

# OpenHPC compiler/mpi designation
. /etc/profile.d/lmod.sh
export OHPC_COMPILER_FAMILY=%{compiler_family}
export OHPC_MPI_FAMILY=%{mpi_family}
. %{_sourcedir}/OHPC_setup_compiler
. %{_sourcedir}/OHPC_setup_mpi

%define doinst() \
pushd src/; \
make %{?_smp_mflags} install %*; \
popd \
pushd lib; \
for static_libs in *.a; do \
    libs=`basename $static_libs .a`; \
    ln -s ${libs}.so.0.0 ${libs}.so; \
    ln -s ${libs}.so.0.0 ${libs}.so.0; \
        rm -f ${libdir}/${static_libs}; \
        cp -dp ${libs}.so* ${libdir}/; \
        rm -f ${libdir}/lib%{base_pname}*.so*; \
done; \
popd

pushd %{base_pname}_%{version}
%{_mpi_load}
export libdir=%{buildroot}%{install_path}/lib
%doinst prefix=%{buildroot}%{install_path} libdir=%{buildroot}%{install_path}/lib
%{_mpi_unload}

pushd %{buildroot}%{install_path}/bin
for prog in *; do
    mv $prog %{base_pname}_$prog
done
popd
pushd %{buildroot}%{install_path}/share/man/man1
rm -f d*
for prog in *; do
    mv $prog %{base_pname}_$prog
done
popd

# Convert the license files to utf8
pushd doc
iconv -f iso8859-1 -t utf-8 < CeCILL-C_V1-en.txt > CeCILL-C_V1-en.txt.conv
iconv -f iso8859-1 -t utf-8 < CeCILL-C_V1-fr.txt > CeCILL-C_V1-fr.txt.conv
mv -f CeCILL-C_V1-en.txt.conv CeCILL-C_V1-en.txt
mv -f CeCILL-C_V1-fr.txt.conv CeCILL-C_V1-fr.txt
popd

popd

# OpenHPC module file
%{__mkdir} -p %{buildroot}%{OHPC_MODULEDEPS}/%{compiler_family}-%{mpi_family}/%{pname}
%{__cat} << EOF > %{buildroot}/%{OHPC_MODULEDEPS}/%{compiler_family}-%{mpi_family}/%{pname}/%{version}
#%Module1.0#####################################################################

proc ModulesHelp { } {

puts stderr " "
puts stderr "This module loads the PETSc library built with the %{compiler_family} compiler"
puts stderr "toolchain and the %{mpi_family} MPI stack."
puts stderr " "

puts stderr "\nVersion %{version}\n"

}
module-whatis "Name: %{pname} built with %{compiler_family} compiler and %{mpi_family} MPI"
module-whatis "Version: %{version}"
module-whatis "Category: runtime library"
module-whatis "Description: %{summary}"
module-whatis "%{url}"

set     version			    %{version}

prepend-path    PATH                %{install_path}/bin
prepend-path    MANPATH             %{install_path}/share/man
prepend-path    INCLUDE             %{install_path}/include
prepend-path	LD_LIBRARY_PATH	    %{install_path}/lib

setenv          %{PNAME}_DIR        %{install_path}
setenv          %{PNAME}_LIB        %{install_path}/lib
setenv          %{PNAME}_INC        %{install_path}/include

EOF

%clean
rm -rf ${RPM_BUILD_ROOT}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc %{base_pname}_%{version}/README.txt %{base_pname}_%{version}/doc/*
%{OHPC_PUB}

%changelog
