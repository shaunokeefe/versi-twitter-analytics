stage {'first': before => Stage['main']}

class apt_get_update {
  exec { '/usr/bin/apt-get -y update':}
}

class {'apt_get_update':
    stage => first,
}

Exec {
    path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
}

class { '::rabbitmq':
}

class { 'mongodb':
    init => 'sysv',
}

class { "python::dev": 
  version => "2.7" 
}

$development_username = "vagrant"
$dev_group = "vagrant"

group {$dev_group:
  ensure => "present",
}

user {'twitter': 
  ensure => present, 
  gid =>$dev_group,
  require => Group[$dev_group],
}

# TODO (shauno): venv should belong to twitter, not dev
class {"python::venv": 
  stage=>main,
  require=>[Class["python::dev"], User[$development_username]],
  owner=>$development_user, 
  group=>$dev_group,
}

python::venv::isolate {"/home/${development_username}/.venv/python":
  require=>Class["python::venv"],
  version=>"2.7",
  requirements=>"/vagrant/requirements.txt"
}

# set up a dev user, vim + git config and dev directory
class { "dev":
  user=>$development_username,
  group=>$dev_group
}
