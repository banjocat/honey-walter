include 'docker'

class honey_walter {

file { ['/app', '/app/honey_walter']:
    ensure => 'directory'
}
->
file { '/app/honey_walter/docker-compose.yml':
    ensure => present,
    source => 'puppet:///modules/honey_walter/docker-compose.yml',
}
->
file { '/app/honey_walter/kibana.yml':
    ensure => present,
    source => 'puppet:///modules/honey_walter/kibana.yml',
}
->
file { '/app/honey_walter/logstash.conf':
    ensure => present,
    source => 'puppet:///modules/honey_walter/logstash.conf',
}
->
file { '/app/honey_walter/nginx.conf':
    ensure => present,
    source => 'puppet:///modules/honey_walter/nginx.conf',
}
->
exec { 'docker_pull':
    command => 'docker-compose -f /app/honey_walter/docker-compose.yml pull',
    path => '/usr/local/bin',
}
->
docker_compose { '/app/honey_walter/docker-compose.yml':
    ensure => present,
}
}
