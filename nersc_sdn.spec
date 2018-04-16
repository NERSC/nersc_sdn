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
This provides a simple daemon that returns a list of running jobs.  It is
used by the API service to cleanup after jobs have finished.


%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/system/
%{__install} -m 0644 sdn_job_server.service $RPM_BUILD_ROOT/usr/lib/systemd/system/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/usr/lib/python2.7/site-packages/nersc_sdn
/usr/lib/python2.7/site-packages/nersc_sdn-0.1-py2.7.egg-info
%config(noreplace missingok) /etc/nersc_sdn.conf.example

%files cli
%defattr(-,root,root)
/usr/bin/sdn_cli

%files server
%defattr(-,root,root)
/usr/bin/initdb.py

%files jobserver
%defattr(-,root,root)
/usr/sbin/sdn_job_server
/usr/lib/systemd/system/sdn_job_server.service

%post server
pip install -y pexpect flask

%changelog
* Fri Apr 13 2018 Shane Canon <scanon@lbl.gov> - 0.1
- Initial release

