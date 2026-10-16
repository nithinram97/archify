import dreamreel as dr

s = dr.Scene("kitchen")
mia, tom, gran = s.cast("mia", "tom", "gran")

mia.sit("chair", already=True)
tom.sit("chair-2", already=True)
mia.feel("happy")
tom.feel("happy")

gran.enter("door").walk_to("front")
gran.turn_to("camera")
gran.say("Has anyone seen my cookies?", mood="surprised")

with s.together():
    mia.look_at(tom)
    tom.look_at(mia)
    mia.feel("scared")
    tom.feel("scared")
s.wait(1.2)
with s.together():
    mia.look_at(gran)
    tom.look_at(gran)
with s.together():
    mia.say("Mice!", mood="scared", to=gran)
    tom.say("Mice!", mood="scared", to=gran, at=s.clock + 0.1)
s.caption("The end", duration=2.5)
s.wait(2.0)
