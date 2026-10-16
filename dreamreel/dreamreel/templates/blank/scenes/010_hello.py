import dreamreel as dr

s = dr.Scene("room")
sam = s.cast("hero")

sam.enter("door").walk_to("center", facing="camera")
sam.do("wave")
sam.say("Hello! This is my first film.", mood="happy")
sam.sit("sofa")
