class honey_walter {

file { '/tmp/honey_walter':
    ensure => 'directory',
}
->
file { ['/app', '/app/honey_walter']:
    ensure => 'directory'
}
->
file { '/app/honey_walter/docker-compose.yml':
    ensure => present,
    source => 'puppet:///modules/honey_walter/docker-compose.yml',
    require => File['/app/honey_walter'],
}

file { '/app/honey_walter/kibana.yml':
    ensure => present,
    source => 'puppet:///modules/honey_walter/kibana.yml',
    require => File['/app/honey_walter'],
}

file { '/app/honey_walter/logstash.conf':
    ensure => present,
    source => 'puppet:///modules/honey_walter/logstash.conf',
    require => File['/app/honey_walter'],
}

file { '/app/honey_walter/nginx.conf':
    ensure => present,
    source => 'puppet:///modules/honey_walter/nginx.conf',
    require => File['/app/honey_walter'],
}
}
