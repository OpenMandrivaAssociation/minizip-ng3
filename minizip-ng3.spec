# (tpg) filter wrong requires
%global __requires_exclude ^.*cmake\\(zlibng\\).*$

%global optflags %{optflags} -O3

# (tpg) enable PGO build
%bcond_without pgo

%define major 3
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

Summary:	Old version of the zip manipulation library
Name:		minizip-ng
Version:	3.0.10
Release:	1
License:	zlib
Group:		System/Libraries
Url:		https://github.com/zlib-ng/minizip-ng
Source0:	https://github.com/zlib-ng/minizip-ng/archive/%{version}/%{name}-%{version}.tar.gz
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	pkgconfig(zlib-ng)
BuildRequires:	pkgconfig(bzip2)
BuildRequires:	pkgconfig(libzstd)
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(openssl)

%description
minizip-ng is a zip manipulation library written in C
that is supported on Windows, macOS, and Linux.

This is an old version, provided for compatibility
with legacy applications only. Use the current version
for new development.

%package -n %{libname}
Summary:	%{summary}
Group:		System/Libraries

%description -n %{libname}
%{description}

%package -n %{develname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Requires:	pkgconfig(zlib-ng)

%description -n %{develname}
Developemt files and headers for %{name}.

%prep
%autosetup -p1

%build
%if %{with pgo}
export LD_LIBRARY_PATH="$(pwd)"

CFLAGS="%{optflags} -fprofile-generate" \
CXXFLAGS="%{optflags} -fprofile-generate" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{build_ldflags} -fprofile-generate" \
%cmake \
    -DMZ_BUILD_TESTS=ON \
    -G Ninja

%ninja_build

LD_PRELOAD=./libminizip.so ./minigzip -9 minizip
LD_PRELOAD=./libminizip.so ./minigzip -d minizip.gz
LD_PRELOAD=./libminizip.so ./minizip test.zip minizip minigzip

unset LD_LIBRARY_PATH
llvm-profdata merge --output=../%{name}-llvm.profdata $(find . -name "*.profraw" -type f)
PROFDATA="$(realpath ../%{name}-llvm.profdata)"
rm -rf *.profraw
ninja clean
cd ..
rm -rf build

CFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
CXXFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
LDFLAGS="%{build_ldflags} -fprofile-use=$PROFDATA" \
%endif
%cmake \
    -DINSTALL_INC_DIR:PATH=%{_includedir}/minizip \
    -G Ninja

%ninja_build

%install
%ninja_install -C build

# For compatibilibty with old minizip
ln -s mz_compat.h %{buildroot}%{_includedir}/minizip/ioapi.h

# No -devel package for compat packages
rm -rf %{buildroot}%{_includedir} \
	%{buildroot}%{_libdir}/cmake \
	%{buildroot}%{_libdir}/pkgconfig \
	%{buildroot}%{_libdir}/*.so

%files -n %{libname}
%{_libdir}/libminizip.so.%{major}*

%if 0
%files -n %{develname}
%{_includedir}/minizip
%dir %{_libdir}/cmake/minizip
%{_libdir}/cmake/minizip/*.cmake
%{_libdir}/libminizip.so
%{_libdir}/pkgconfig/minizip.pc
%endif
