;Header and description

(define (domain Smarted)

;remove requirements that are not needed
(:requirements :strips :fluents :typing :negative-preconditions :disjunctive-preconditions :equality)

(:types 
floor 
fanmotor 
light 
buzzer 
mail_report 
message
pillar
;todo: enumerate types and their hierarchy here, e.g. car truck bus - vehicle
;types of inputs- sensors of various types, various rooms and floors
;sensor
;types for actuators/outputs
)

; un-comment following line if constants are needed
;(:constants )

(:predicates ;todo: define predicates here
        (structure-monitor)
        (ambience-monitor)
        (off ?mr1 - mail_report)
        (off1 ?b - buzzer)
        (off2 ?l - light)
        (off3 ?mtr - fanmotor)
        (send ?h - message)

)


(:functions ;todo: define numeric functions here

        (piezo ?f - floor)
        (humidity ?f - floor)
        (co2 ?f - floor)(temperature ?f - floor)
        (flame ?f - floor)
        (lux ?f - floor)
            (threshold_co2)
            (threshold_piezo)
            (threshold_humidity_min)
            (threshold_humidity_max)
            (threshold_flame)
            (threshold_lux)
            (threshold_temp_min)
            (threshold_temp_max)

)


(:action send-mail
    :parameters (?f - floor ?h - message ?mr1 - mail_report)
    :precondition (or (off ?mr1)
                  (>(piezo ?f) (threshold_piezo)) 
                  (>(flame ?f)(threshold_flame))
                  (>(co2 ?f) (threshold_co2)))
    :effect (and (not(off ?mr1))(send ?h)(structure-monitor))
)

(:action all-in-control
    :parameters (?f - floor ?h - message ?mr1 - mail_report)
    :precondition (or (<(piezo ?f) (threshold_piezo))
                  (<(co2 ?f) (threshold_co2)) 
                  (<(flame ?f)(threshold_flame)))
    :effect (and (off ?mr1)(send ?h)(structure-monitor))
)


(:action notify-emergency
    :parameters (?f -floor ?h - message ?b - buzzer)
    :precondition (or (off1 ?b)
                  (>(co2 ?f) (threshold_co2))
                  (<(flame ?f)(threshold_flame))
                  (>(piezo ?f) (threshold_piezo)))
    :effect (and (not(off1 ?b)) (send ?h)(structure-monitor))
)


(:action temperature-control-off
    :parameters (?f -floor ?h - message ?mtr - fanmotor)
    :precondition (or (off3 ?mtr)
                  (and (>(humidity ?f) (threshold_humidity_min))
                  (<(humidity ?f) (threshold_humidity_max)))
                  (and (>(temperature ?f) (threshold_temp_min))
                  (<(temperature ?f) (threshold_temp_max)))
                  (<(co2 ?f) (threshold_co2)))
    :effect (and (send ?h)(structure-monitor))
)


(:action temperature-control-on
    :parameters (?f -floor ?h - message ?mtr - fanmotor)
    :precondition (or (off3 ?mtr)
                  (>(humidity ?f) (threshold_humidity_max))
                  (>(temperature ?f) (threshold_temp_max))
                  (>(co2 ?f) (threshold_co2)))
    :effect (and (not(off3 ?mtr))(send ?h)(ambience-monitor))
)


(:action leicht-control-off
    :parameters (?f - floor ?h - message ?l - light)
    :precondition (or (off2 ?l)
                  (>(lux ?f) (threshold_lux)))
    :effect (and (off2 ?l) (send ?h) (ambience-monitor))
)

(:action leicht-control-on
    :parameters (?f -floor ?h - message ?l - light)
    :precondition (or (off2 ?l)
                  (<(lux ?f) (threshold_lux)))
    :effect (and (not(off2 ?l))(send ?h)(ambience-monitor))
)


(:action safe-state-no-emergency
    :parameters (?f -floor ?h - message ?mtr - fanmotor ?b - buzzer)
    :precondition (or(<(co2 ?f) (threshold_co2))
                  (=(flame ?f)(threshold_flame))
                  )
     :effect (and (off3 ?mtr) (off1 ?b) (send ?h)(ambience-monitor))
)
)