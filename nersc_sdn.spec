%define name nersc_sdn
%define version 0.3.2
%define unmangled_version 0.3.2
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
%if 0%{?suse_version} > 0
Requires: python-gunicorn, python-pymongo, python-pexpect, nersc_sdn, python-flask
%else
Requires: python-gunicorn, python-pymongo, python-pip, nersc_sdn, python-flask
%endif


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
%{__install} -m 0644 sdn_job_server.service %{buildroot}%{_unitdir}/sdn_job_server.service
%{__install} -m 0644 sdn_api.service %{buildroot}%{_unitdir}/sdn_api.service
mkdir -p $RPM_BUILD_ROOT/var/log/sdnapi/




%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/usr/lib/python2.7/site-packages/nersc_sdn
/usr/lib/python2.7/site-packages/nersc_sdn-%{version}-py2.7.egg-info
%config(noreplace missingok) /etc/nersc_sdn.conf.example

%files cli
%defattr(-,root,root)
/usr/bin/sdn_cli

%files server
%defattr(-,root,root)
%{_libexecdir}/nersc_sdn/sdninitdb
%{_unitdir}/sdn_api.service
%dir %attr(700,sdnapi,sdnapi) /var/log/sdnapi

%files jobserver
%defattr(-,root,root)
%attr(755,root,root) /usr/sbin/sdn_job_server
/usr/lib/systemd/system/sdn_job_server.service

%pre server
/usr/sbin/groupadd -r sdnapi >/dev/null 2>&1 || :
/usr/sbin/useradd -M -N -g sdnapi -r -d /var/lib/sdnapi -s /bin/bash \
    -c "SDNAPI Server" sdnapi >/dev/null 2>&1 || :

%post server
%if 0%{?suse_version} < 1
pip install -y pexpect
%endif

%changelog
* Mon Oct 01 2018 Shane Canon <scanon@lbl.gov> - 0.3.2
- Added key file option for ssh

* Sun Jul 15 2018 Shane Canon <scanon@lbl.gov> - 0.3.1
- Added service files

* Sat Jun 09 2018 Shane Canon <scanon@lbl.gov> - 0.3
- Added ddns support

* Sat May 12 2018 Shane Canon <scanon@lbl.gov> - 0.2
- Bug Fixes and renamed initdb

* Fri Apr 13 2018 Shane Canon <scanon@lbl.gov> - 0.1
- Initial release

