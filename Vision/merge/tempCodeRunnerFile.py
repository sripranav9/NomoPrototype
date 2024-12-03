    if num_people >= 3:
                    print(f"{num_people} people detected! \nMoving back and closing eyes.")
                elif (num_people < 3 and num_people > 0) and gesture_detected == "Open_Palm":
                    print(f"{num_people} people detected with an open palm! \nWaving Back! Hii!")
                elif (num_people < 3 and num_people > 0) and gesture_detected == "Thumb_Up":
                    print(f"{num_people} people detected with a thumbs-up! \nCheers!")
                elif (num_people < 3 and num_people > 0) and gesture_detected == "Closed_Fist":
                    if closed_fist_counter == 1:
                        print(f"Starting desk mode!")
                        closed_fist_counter = 0
                    else:
                        print(f"{num_people} people detected with closed fist. \nChecking for desk mode.")
                        closed_fist_counter += 1
                elif num_people == 0 and gesture_detected:
                    print(f"{gesture_detected} detected. Where's your face human? \nAre you a ghost?")
                elif num_people > 0:
                    print(f"{num_people} people detected. Awaiting interaction...")
                else:
                    cont