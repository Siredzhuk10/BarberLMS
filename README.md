<h1>SIMPLE LMS APP BASED ON DJANGO AND POSTGRESQL</h1>
<h2>The LMS Has Minimum Templates, It's only for backend educational purpose, with several url that i have put on the urls.py</h2>
<h2>It's also can be virtualized using a docker, that's why there is a dockerfile and docker-compose.yml in there</h2>
<br>
<h2>Here is how you run it on docker container</h2>
<ul>
  <li>Install Docker If You Don't Have It. If You Already Have It, Run Docker Machine </li>
  <li>Then download zip of the project, extract it on your computer</li>
  <li>Before you run anything, i suggested you to download extension docker (by microsoft) and postgre (by weijan chen). I Use VSCODE Btw For The IDE</li>
  <li>Open new terminal, then Run these command below</li>
  <li>docker compose up -d --build</li>
  <li>It Will Take Maybe Couple Minutes To Compose It</li>
  <li>If Already Running, Then Open The Docker Extension On VSCODE To See The Running Container </li>
  <li>Then Press Right Click On "docker-lms-django" . Select Attach Shell to make new docker terminal</li>
  <li>Before You Run Anything On Terminal, You Should Connect To Postgre First</li>
  <li>Open Your Postgre Extension, Then Make A New Connection </li>
  <li>Fill The Database Name, Database User, and Password Based On File Settings.py. You can search the file first, then scrolldown to databases section </li>
  <li>After Make Connection Turn To Next Step </li>
  <li>Then run these commands below</li>
  <li>python manage.py makemigrations</li>
  <li>python manage.py migrate</li>
  <li>Those Commands Is For Making A Migration To Make A Table On Postgree</li>
  <li>To check it, use the postgre extension again. Then check it on table user, coursecontent, coursemember, course, and comment</li>
  <li>After That, Go To Docker Terminal and type command below</li>
  <li>python manage.py runserver 0.0.0.0:8000</li>
  <li>To Look The Data, Just Simply Call The URL That I've been Set On Urls.py</li>
  
</ul>
