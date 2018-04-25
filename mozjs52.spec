%global pre_release %{nil}
%define pkgname mozjs
%define api 52.7
%define libmozjs %mklibname %{pkgname} %{api}
%define libmozjs_devel %mklibname %{pkgname} %{api} -d
%define major %(echo %{version} |cut -d. -f1)

Summary:	JavaScript interpreter and libraries
Name:		mozjs52
Version:	52.7.4
Release:	1
License:	MPLv2.0 and BSD and GPLv2+ and GPLv3+ and LGPLv2.1 and LGPLv2.1+
URL:		https://developer.mozilla.org/en-US/docs/Mozilla/Projects/SpiderMonkey/Releases/%{major}
Source0:	https://queue.taskcluster.net/v1/task/U1nRqVKNRj29NR92pluyxA/runs/0/artifacts/public/build/mozjs-%{version}.tar.bz2
BuildRequires:	pkgconfig(icu-i18n)
BuildRequires:	pkgconfig(nspr)
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(zlib)
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
%setup -q -n mozjs-%{version}/js/src

%build
# Need -fpermissive due to some macros using nullptr as bool false
export CFLAGS="%{optflags} -fpermissive"
export CXXFLAGS="$CFLAGS"
export CC=gcc
export CXX=g++

# Kind of, but not 100%, like autoconf...
./configure \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--with-system-nspr \
	--enable-readline \
	--enable-shared-js \
	--enable-optimize \
	--with-system-zlib \
	--with-system-icu \
	--without-intl-api
%make

%install
%makeinstall_std

chmod a-x  %{buildroot}%{_libdir}/pkgconfig/*.pc

# Do not install binaries or static libraries
rm -f %{buildroot}%{_libdir}/*.a %{buildroot}%{_bindir}/js*

# Install files, not symlinks to build directory
pushd %{buildroot}%{_includedir}
    for link in `find . -type l`; do
	header=`readlink $link`
	rm -f $link
	cp -p $header $link
    done
popd
cp -p js/src/js-config.h %{buildroot}%{_includedir}/mozjs-%{major}

%check
# Some tests will fail
tests/jstests.py -d -s --no-progress ../../js/src/js/src/shell/js || :

%files -n %{libmozjs}
%{_libdir}/*.so
%{_libdir}/*.ajs

%files -n %{libmozjs_devel}
%doc ../../LICENSE ../../README
%{_libdir}/pkgconfig/*.pc
%{_includedir}/mozjs-%{major}
