%define name nersc_sdn
%define version 0.1
%define unmangled_version 0.1
%define release 1

Summary: NERSC's SDN API service to dynamically create routes to HPC compute nodes
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: BSD
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Requires: python-requests
Vendor: Shane Canon <scanon@lbl.gov>
Url: http://www.nersc.gov

%description
NERSC's SDN API service base package


%package cli
Summary: NERSC's SDN API CLI tool

%description cli
NERSC's SDN API CLI tool
Requires: nersc_sdn

%package server
Summary: NERSC's SDN API Server
Requires: python-gunicorn, python-pymongo, python-pip, nersc_sdn

%description server
NERSC's SDN API service to dynamically create routes to HPC compute nodes

%package jobserver
Summary: NERSC's SDN API Job Server

%description jobserver
NERSC's SDN API job service to provide a list of running jobs to the SDN API
service.

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/usr/lib/python2.6/site-packages/nersc_sdn
/usr/lib/python2.6/site-packages/nersc_sdn-0.1-py2.6.egg-info
/etc/nersc_sdn.conf.example

%files cli
%defattr(-,root,root)
/usr/bin/cli.py

%files server
%defattr(-,root,root)
/usr/bin/initdb.py

%files jobserver
%defattr(-,root,root)
/usr/sbin/job_server.py

%post server
pip install -y pexpect flask
