stage {'first': before => Stage['main']}

$repo_directory = "/opt/twitter/twitter_scraper"

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

$username = "twitter"
$group = "twitter"

group {$group:
  ensure => "present",
}

user {'twitter': 
  ensure => present, 
  gid =>$group,
  managehome=>true,
  require => Group[$group],
}

# TODO (shauno): venv should belong to twitter, not dev
class {"python::venv": 
  stage=>main,
  require=>[Class["python::dev"], User[$username]],
  owner=>$username, 
  group=>$group,
}

python::venv::isolate {"/home/${username}/.venv/python":
  require=>Class["python::venv"],
  version=>"2.7",
  requirements=>"${repo_directory}/requirements.txt"
}
