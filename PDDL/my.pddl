(define(problem monitor) 
        (:domain Smarted)
(:objects 
    ;actuators
    mtr - fanmotor
    b - buzzer
    l - light
    h - message
    f - floor
    mr1 - mail_report
    p - pillar
)

(:init
    ;todo: put the initial state's facts and numeric values here
    (off mr1)
    ;(at-mail_report mr1 f)
    ;(at-chutemotor mtr f)
    (off1 b)
    ;(at-buzzer b f)
    (off2 l)
    (off3 mtr)
    ;(at-light l f)
    ;thresholds for sensors
    (= (threshold_piezo) 16)
    (= (threshold_humidity_min) 40)
    (= (threshold_humidity_max) 60)
    (= (threshold_temp_min) 40)
    (= (threshold_temp_max) 60)
    (= (threshold_co2) 800)
    (= (threshold_flame) 1)
    (= (threshold_lux) 700)
    
    
    ;current sensor values
    
    (= (flame f) 5)
    (= (lux f) 2)
    (= (piezo f) 3)
    (= (humidity f) 4)
    (= (temperature f) 1)
    (= (co2 f) 6)
    ;(= (threshold_light_max) 1000)
)

(:goal (and
        (structure-monitor)
        (ambience-monitor)
)
)
)