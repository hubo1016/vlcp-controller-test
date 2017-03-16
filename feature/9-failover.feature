Feature: failover
    Scenario: controller start, there is no bridge
        given remove bridge "host1"
        when restart controller "host1"
        then check get all bridge info "host1"
        then add bridge "host1"