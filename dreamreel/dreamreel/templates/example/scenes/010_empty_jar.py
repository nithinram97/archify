import dreamreel as dr

s = dr.Scene("kitchen")
mia, tom = s.cast("mia", "tom")
s.title_card("The Last Cookie")

tom.sit("chair-2", already=True)
tom.look_at("window")

mia.enter("door").walk_to("counter")
mia.feel("surprised")
s.wait(0.6)
mia.turn_to(tom)
mia.say("Tom. The cookie jar is empty.", mood="worried", to=tom)
tom.look_at(mia)
tom.say("Is it? How strange.", mood="worried", to=mia)

mia.walk_to("table", facing=tom)
mia.say("There were twelve cookies this morning.", mood="angry", to=tom)
tom.do("shrug")
tom.say("Maybe... mice?", to=mia)
mia.say("Mice. With crumbs on their face?", mood="smug", to=tom)
tom.do("facepalm")

tom.stand()
tom.turn_to(mia)
tom.say("Okay, okay! I saved you one.", mood="happy", to=mia)
with s.together():
    mia.feel("excited")
    mia.do("cheer")
mia.say("The last cookie!", mood="happy", to=tom)
