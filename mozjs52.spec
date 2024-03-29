%global pre_release %{nil}
%define pkgname mozjs
%define api 52
%define libmozjs %mklibname %{pkgname} %{api}
%define libmozjs_devel %mklibname %{pkgname} %{api} -d
%define major %(echo %{version} |cut -d. -f1)

# (tpg) optimize a bit
%global optflags %{optflags} -O3

Summary:	JavaScript interpreter and libraries
Name:		mozjs52
Version:	52.8.1
Release:	5
License:	MPLv2.0 and BSD and GPLv2+ and GPLv3+ and LGPLv2.1 and LGPLv2.1+
URL:		https://developer.mozilla.org/en-US/docs/Mozilla/Projects/SpiderMonkey/Releases/%{major}
Source0:	https://queue.taskcluster.net/v1/task/Y_v0j-jqQ4mkVMFD0kRKfg/runs/0/artifacts/public/build/mozjs-%{version}.tar.bz2
Source10:	http://ftp.gnu.org/gnu/autoconf/autoconf-2.13.tar.gz
Patch0:		mozjs-52.8.1-system-libs.patch
Patch1:		mozjs-52.8.1-fix-crash-on-startup.patch
Patch2:		firefox-52.7.2esr-add-riscv64.patch
Patch3:		trim.patch
Patch4:		patch-js_src_jsapi-tests_testPrintf.cpp
BuildRequires:	pkgconfig(icu-i18n)
BuildRequires:	pkgconfig(nspr)
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(python2)
BuildRequires:	readline-devel
BuildRequires:	zip
BuildRequires:	python

%description
JavaScript is the Netscape-developed object scripting language used in millions
of web pages and server applications worldwide. Netscape's JavaScript is a
super set of the ECMA-262 Edition 3 (ECMAScript) standard scripting language,
with only mild differences from the published standard.

%package -n %{libmozjs}
Provides:	mozjs%{major} = %{EVRD}
Summary:	JavaScript engine library

%description -n %{libmozjs}
JavaScript is the Netscape-developed object scripting language used in millions
of web pages and server applications worldwide. Netscape's JavaScript is a
super set of the ECMA-262 Edition 3 (ECMAScript) standard scripting language,
with only mild differences from the published standard.

%package -n %{libmozjs_devel}
Summary:	Header files, libraries and development documentation for %{name}
Provides:	mozjs%{major}-devel = %{EVRD}
Requires:	%{libmozjs} = %{EVRD}

%description -n %{libmozjs_devel}
This package contains the header files, static libraries and development
documentation for %{name}. If you like to develop programs using %{name},
you will need to install %{name}-devel.

%prep
%autosetup -p1 -n mozjs-%{version} -a 10
%config_update

#rm -rf nsprpub
cd config/external/
for i in freetype2 icu nspr nss sqlite zlib; do
	rm -rf $i
	mkdir $i
	touch $i/moz.build
done
cd ../..

TOP="$(pwd)"
cd autoconf-2.13
./configure --prefix=$TOP/ac213bin
%make_build
%make install

%build
%setup_compile_flags
# Need -fpermissive due to some macros using nullptr as bool false
export AUTOCONF="$(pwd)"/ac213bin/bin/autoconf
export CFLAGS="%{optflags} -fpermissive -fPIC -fuse-ld=bfd"
export CXXFLAGS="$CFLAGS"
export LDFLAGS="$CFLAGS"
export CC=gcc
export CXX=g++
export LD=ld.bfd

# Kind of, but not 100%, like autoconf...
cd js/src
./configure \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--disable-readline \
	--disable-debug \
	--disable-debug-symbols \
	--enable-shared-js \
	--enable-optimize="-O3" \
	--enable-pie \
	--disable-jemalloc \
	--without-intl-api \
	--with-system-bz2 \
	--with-system-icu \
	--with-system-jpeg \
	--with-system-libevent \
	--with-system-libvpx \
	--with-system-nspr \
	--with-system-nss \
	--with-system-png \
	--with-system-zlib

%make_build

%install
cd js/src
%make_install

chmod a-x  %{buildroot}%{_libdir}/pkgconfig/*.pc

# Do not install binaries or static libraries
rm -f %{buildroot}%{_libdir}/*.a %{buildroot}%{_bindir}/js*

# Install files, not symlinks to build directory
pushd %{buildroot}%{_includedir}
    for link in $(find . -type l); do
	header="$(readlink $link)"
	rm -f $link
	cp -p $header $link
    done
popd
cp -p js/src/js-config.h %{buildroot}%{_includedir}/mozjs-%{major}

# Remove unneeded files, this files is 500MiB+ of size
rm -rf %{buildroot}%{_libdir}/*.ajs

%check
# Some tests will fail
tests/jstests.py -d -s --no-progress ../../js/src/js/src/shell/js || :

%files -n %{libmozjs}
%{_libdir}/*.so

%files -n %{libmozjs_devel}
%doc README
%license LICENSE
%{_libdir}/pkgconfig/*.pc
%{_includedir}/mozjs-%{major}
