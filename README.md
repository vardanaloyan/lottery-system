# Lottery System application
This is assignment exercise.
The goal of this exercise is to build lottery system application.

Requirements

- The service will allow anyone to register as a lottery participant.
- Lottery participants will be able to submit as many lottery ballots for any lottery that isn’t yet finished.
- Each day at midnight the lottery event will be considered closed and a random lottery winner will be selected from all participants for the day.
- All users will be able to check the winning ballot for any specific date.
- The service will have to persist the data regarding the lottery.
- Please put focus on the domain model of this problem it deserve attention.

## How to BUILD and RUN
It assumes that you already have downloaded or cloned repository

```bash
# Move into the working directory
cd lottery-system
```
```bash
# Build docker-compose file
docker-compose -f docker-compose.yml build
```

```bash
# Run docker-compose file
docker-compose -f docker-compose.yml up
```
In terminal you will see something like this

```bash
 % docker-compose -f docker-compose.yml up
Starting lottery_system_lottery-system_1 ... done
Attaching to lottery_system_lottery-system_1
lottery-system_1  | [2021-10-04 11:23:53 +0000] [1] [INFO] Starting gunicorn 20.1.0
lottery-system_1  | [2021-10-04 11:23:53 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
lottery-system_1  | [2021-10-04 11:23:53 +0000] [1] [INFO] Using worker: gthread
lottery-system_1  | [2021-10-04 11:23:53 +0000] [9] [INFO] Booting worker with pid: 9
lottery-system_1  | 2021-10-04 11:23:53,537 : INFO : Scheduler started
lottery-system_1  | 2021-10-04 11:23:53,586 : INFO : Added job "midnight_award" to job store "default"
```
Click [http://0.0.0.0:8080](http://0.0.0.0:8080) to navigate to the application

## HOW TO USE THE APPLICATION

If there's no authenticated users yet (There's no Session ID in browsers Cookies), user will be redirected to `login` page

![image](./lottery_system/docs/images/Lottery-System-screenshot.png)

First, user needs to register. Click _Sign Up here_ text for the registration and fill your desired username and password and click *Sign Up*

![image](./lottery_system/docs/images/Lottery-System-Sign-Up.png)

---

After successful registration and login, user will see this

![image](./lottery_system/docs/images/Lottery-System-main-page.png)

Here are showing all active lotteries and ballots number corresponding to the lotteries.

---

For submitting ballots user needs to click onto the lottery (example 2x time "Big Chance" and 1x time on "Extra Win")

![image](./lottery_system/docs/images/Lottery-System-Submit.png)
 
In the above image, user Vardan submitted 2 ballots for "Big Chance", and 1 ballot for "Extra Win" Lottery

---

In Check Winner page, user can check the winner ballots, by specifying the date

![image](./lottery_system/docs/images/Lottery-System-Check-Winner.png)

Example

![image](./lottery_system/docs/images/Lottery-System-Check-Winner-2.png)

---

## How to STOP and CLEAN-UP

```bash
# Stop running docker-compose container and clean-up
# ctrl+c # Keyboard Interrupt will stop running container
docker-compose -f docker-compose.yml down # clean up
```
