from robot_utils import *


def main():
	measures = []
	for count in range(0, 250):
		(lV, rV) = robot.distance()
		sonic = robot.ultrasound()
		measure = (lv, sonic, rV)
		print(measure)
		measures.append(measure)
	
	room = input("Room number? ")
	file = open("room_{}".format(room))
	file.write(measures)
	file.close()
	print("Done")

if __name__ == "__main__":
	main()