import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from contacts.models import Contact

DIRECTORY_TEXT = """
Senior Accountant in Finance
Dubai - Head Office | 3:23 PM local
time
PIXL
0566409359
Mohammad Jabed Aalam jabed@invespy.com Reports to Suman Kumari
Company Driver in CEO
Dubai - Head Office | 3:23 PM local
time
PIXL
526605885
Rexi Abesekara rexi@pixl.ae Reports to Rashmi Kapale
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 58 279 5769
Prince Abongnuk prince@invespy.com Reports to Owais Khan
Sales Associate in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
Ayesha Aftab ayesha@invespy.com Reports to Amogh Desmukh
Project Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 589880925
Ahmed Agiza ahmed@invespy.com Reports to Owais Khan
2 direct reports
FP & A Analyst in Finance
Dubai -Other location | 3:23 PM
local time
Quattro
+971561669451
0561669451
Nikhil Agrawal nikhil@pixl.ae Reports to Suman Kumari
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 1/23
Senior Designer in Creative
Pakistan
Creative
Reports to Pierre Van der
Merwe
Bilal Ahmad bilal@pixl.ae
Sales Executive in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971555201578
Khaled Ahmed khaled@invespy.com Reports to Mubeen Iqbal
Tele Sales Executive in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971 55 961 9500
Rizwan Ahmed rizwan@invespy.com Reports to Amogh Desmukh
Manager- Business Growth & Client
Relations in Sales
Dubai - Head Office | 3:23 PM local
time
PIXL
0562445541
Reports to Nishanth
Kakkamani
Abdullah Al-Mohammedi abdullah.a@pixl.ae
Copywriter in Content
Dubai - Head Office | 323 PM local
time
PIXL
971 50 124 5096
Marah Alachkar marah@pixl.ae Reports to Azra Sulthana
OUT DEC 4-11
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 58 164 1224
Mohammad Albeetar mohammad.a@invespy.com Reports to Azad Attar
Senior Accountant in Finance
Dubai - Head Office | 3:23 PM local
time
PIXL
Naushad Ali naushad@pixl.ae Reports to Suman Kumari
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 2/23
Administrator in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971554679383
Eugiel Alquizar eugiel@invespy.com Reports to Owais Khan
Procurement Manager in Finance
Dubai - Head Office | 3:23 PM local
time
PIXL
+971 52 563 0860
Rajakumar Reports to Suman Kumari i Ambati rajakumari@pixl.ae
Editor in Content
India | 4:53 PM local time
PIXL
+91 90619 30892
Reports to Habeeb Mohammed
Ismail
Karthik Anoop karthik@invespy.com
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 55 746 5558
Hamza Asad hamza@invespy.com Reports to Toby Mishon
Project Manager in Sales
Dubai - Head Office | 3:23 PM local
time
Invespy
Sherief Aslan Sherief@invespy.com Reports to Owais Khan
4 direct reports
Project Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 58 945 6493
Azad Attar azad@invespy.com Reports to Owais Khan
4 direct reports
Administrator in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 50 464 9813
Ryland Austria ryland@invespy.com Reports to Owais Khan
Social Media Manager - Content in
Creative
Dubai - Head Office | 3:23 PM local
time
+96171001959
0523462506
Mandy Azzi mandy@pixl.ae Reports to Azra Sulthana
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 3/23
B
PIXL
CEO of Property Time in Property
Time
Dubai - Head Office | 3:23 PM local
time
Property Time
0585463838
Binesh Babu bpanicker@propertytime.ae Reports to Imran Khan
1 direct report
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971526950030
Nadiya Bacharni nadiya@invespy.com Reports to Toby Mishon
IT Executive in Operations
Dubai - Head Office | 3:23 PM local
time
PIXL
+971521374423
Shainal Badusha shainal@pixl.ae Reports to Rashmi Kapale
Senior Manager - Channel
Relationship in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971 58 580 0759
Arjun Balagopal arjun.b@invespy.com Reports to Amogh Desmukh
Account Executive in Account
Management
Dubai - Head Office | 3:23 PM local
time
PIXL
502882107
Divya Balakrishnan divya@pixl.ae Reports to Raneen Zaatarah
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 56 896 6388
Luliia Baranovska iuliia@invespy.com Reports to Navid Rashid
Channel Relationship Manager in
Invespy
Dubai - Head Office | 3:23 PM local
time
0527058673
Mounya Barich mounya@invespy.com Reports to Amogh Desmukh
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 4/23
Invespy
Administrator in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 55 974 3548
Art Barrero art@invespy.com Reports to Owais Khan
Relationship Manager in Sales
Dubai -Other location | 3:23 PM
local time
Quattro
Reports to Mohammad
Motavasel
Elnaz Barzegari elnaz@quattro-capital.com
Media Manager in Sales
Dubai - Head Office | 3:23 PM local
time
PIXL
0565981697
Monisha Baskar Monisha@pixl.ae Reports to Saloni Rohatgi
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 56 730 0932
Beah Beah ahmed.b@invespy.com Reports to Ahmed Agiza
dummy employee
Dubai - Head Office | 3:23 PM local
time
PIXL
Panda Bear zeeshan@invespy.com Reports to Imran Khan
Sales Operations Executive in
Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971502935501
Venn Bedayo wilven@invespy.com Reports to Owais Khan
Receptionist/ Office Assistant in
Human Resources
Dubai - Head Office | 3:23 PM local
time
PIXL
0554531740
Kate Benas kate@pixl.ae Reports to Rashmi Kapale
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 5/23
C
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 56 909 5115
Manahil Bhat Reports to Azad Attar ti manahil@invespy.com
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971545393060
Assia boudfel Boudfel assia@invespy.com Reports to Sherief Aslan
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 58 516 2658
Carla Butler carla@invespy.com Reports to Sherief Aslan
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 50 348 1494
Nancy Cabanillas nancy@invespy.com Reports to Navid Rashid
Barista in Operations
Dubai - Head Office | 3:23 PM local
time
PIXL
Chazel Carnero chazel@pixl.ae Reports to Rashmi Kapale
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 52 472 2404
Alejandro Ceron alejandro@invespy.com Reports to Henry Martin
Content Creator in Creative
Dubai - Head Office | 3:23 PM local
time
PIXL
+971 58 588 7132
Harshyy Chandwani harshul@pixl.ae Reports to Azra Sulthana
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 6/23
D
E
Director in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 58 667 0543
Amer Chaudhary amer@invespy.com Reports to Imran Khan
Head- PR in PR
Dubai - Head Office | 3:23 PM local
time
PIXL
Debanjana Chaudhuri deb@pixl.ae Reports to Imran Khan
3 direct reports
Office Boy in Operations
Dubai - Head Office | 323 PM local
time
PIXL
Mike Cortiz mike@pixl.ae Reports to Rashmi Kapale
OUT NOV 28-JAN 5
Director in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971586748706
Amogh Desmukh amogh@invespy.com Reports to Imran Khan
13 direct reports
Director in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971 50 580 1343
Amitabh Dhawan amitabh@invespy.com Reports to Imran Khan
Marketing Executive in Marketing
Dubai - Head Office | 3:23 PM local
time
PIXL
+971 55 527 4699
Gouthami Durgasi gouthami@pixl.ae Reports to Saloni Rohatgi
Data Integration Specialist in
Integration and Tech Support
Philippines
Technology Group
+639672663595
Reports to Venkatesan
Rajagopal
Lixx Edmund Madamesila felix@pixl.ae
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 7/23
F
G
Tele Sales Executive in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971564237147
Asmaa Elmahdy asmaa@invespy.com Reports to Amogh Desmukh
Sales Manager in Invespy
Dubai -Other location | 323 PM
local time
Invespy
971507031294
971507031294
Rawan Elsanoucy rawan@invespy.com Reports to Toby Mishon
OUT DEC 10-19
Account Manager in Account
Management
Dubai - Head Office | 3:23 PM local
time
PIXL
+971 56 592 6728
Nadine Elwakdy nadine@pixl.ae Reports to Omnia Mohammed
Senior Manager - Channel
Relationship in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971 54 402 5210
Stuart Flynn stuart@invespy.com Reports to Amogh Desmukh
4 direct reports
Digital Marketing Manager in
Performance
India | 4:53 PM local time
PIXL
Neha Gaba neha@pixl.ae Reports to Prasad Sawant
Admin Executive in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
0507341013
Jo dela Fuente Geronimo xyza@invespy.com Reports to Owais Khan
Graphic Designer in Creative
Pakistan
PIXL
+923464449176
+923464449176
Numan Ghani numan@pixl.ae Reports to Fahad Khan
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 8/23
H
I
Account Executive in Account
Management
Dubai - Head Office | 323 PM local
time
PIXL
0502564747
Haider Habib haider@pixl.ae Reports to Urooj Husain
OUT DEC 8-22
Business Systems Manager in
Technology Group
Dubai - Head Office | 3:23 PM local
time
Technology Group
Reports to Venkatesan
Rajagopal
Omer Hamid omer@pixl.ae
Social Media Designer in Creative
Dubai - Head Office | 3:23 PM local
time
PIXL
+971526031024
+971526031024
Kashmala Hat Reports to Azra Sulthana tan kashmala@pixl.ae
Video Content Creator in Content
Dubai - Head Office | 3:23 PM local
time
PIXL
+971564995653
Aruna Herath aruna@pixl.ae Reports to Azra Sulthana
Administrator in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971545151887
Marvie Hingpit marvie@invespy.com Reports to Owais Khan
Director- Client Success in Account
Management
Dubai - Head Office | 3:23 PM local
time
PIXL
0588853448
0527769622
Urooj Husain urooj@pixl.ae Reports to Omnia Mohammed
1 direct report
Tele Sales Executive in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 52 778 6643
Taufique Hussain taufique@invespy.com Reports to Amogh Desmukh
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 9/23
J
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 55 659 7663
Einas Ibrahim einas@invespy.com Reports to Owais Khan
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971504703009
Fatima Imran fatima@invespy.com Reports to Toby Mishon
Project Manager in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971521011370
Mubeen Iqbal mubeen@invespy.com Reports to Owais Khan
2 direct reports
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 56 600 5454
Alaa Jabbour alaa@invespy.com Reports to Owais Khan
Event Coordinator in Events
Dubai - Head Office | 3:23 PM local
time
PIXL
+971527812298
Maria Jacob maria@pixl.ae Reports to Rashmi Kapale
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971543100309
Antigona Jahaj antigona@invespy.com Reports to Owais Khan
Relationship Manager in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971 58 588 7120
Anshu Jain anshu@invespy.com Reports to Amogh Desmukh
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 10/23
K
Performance Copywriter in Content
India | 4:53 PM local time
PIXL
9643418826
Deepanshu Jangid deepanshu@pixl.ae Reports to Azra Sulthana
Paid Media Executive in
Performance
Gurgaon, India | 4:53 PM local time
PIXL
+919599174307
Lisha Jindal lisha@pixl.ae Reports to Prasad Sawant
Sales Manager in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
Carmen Joseph carmen@invespy.com Reports to Owais Khan
FB Ads Specialist in Performance
Gurgaon, India | 4:53 PM local time
Invespy
9766188479
Prashant Joshi prashant@pixl.ae Reports to Prasad Sawant
Administrator in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 50 230 6980
Annie Justin annie@invespy.com Reports to Owais Khan
Relationship Manager in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971 52 508 5389
Ergena Kaci ergena@invespy.com Reports to Stuart Flynn
Sales Manager in Sales
Dubai - Head Office | 3:23 PM local
time
PIXL
+971 52 965 3567
Nishanth Kakkamani nishanth@pixl.ae Reports to Imran Khan
3 direct reports
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 11/23
HR Business Partner in Human
Resources
Dubai - Head Office | 3:23 PM local
time
PIXL
+971522436879
Rashmi Kapale rashmi@pixl.ae Reports to Imran Khan
12 direct reports
Sales Manager in Sales
Dubai - Head Office | 3:23 PM local
time
Invespy
585255909
Leyli Kazyohan leyli@invespy.com Reports to Owais Khan
Sales Manager in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971 58 540 8939
Jacob Kerrecoe jacob@invespy.com Reports to Henry Martin
Sales Manager in Sales
Dubai -Other location | 323 PM
local time
Invespy
971 58 568 2493
Pruthvi Khade pruthvi@invespy.com Reports to Azad Attar
OUT DEC 1-19
Graphic Designer in Creative
Pakistan
Property Time
Hamid Khan hamid.khan@propertytime.ae Reports to Binesh Babu
CEO in CEO
Dubai - Head Office | 3:23 PM local
time
PIXL
+971504107307
Imran Khan imran@pixl.ae 15 direct reports
Operations Executive in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
0525204959
+971505933962
Zaid Khan mohiuddin@invespy.com Reports to Amogh Desmukh
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 12/23
Senior Art Director in Design
Dubai - Head Office | 3:23 PM local
time
Creative
0504354454
Reports to Pierre Van der
Merwe
Fahad Khan fahad@pixl.ae
3 direct reports
Director in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
971555435670
Owais Khan owais@invespy.com Reports to Imran Khan
32 direct reports
Sales Associate in Invespy
USA
Invespy
Safi Khan Safi@invespy.com Reports to Owais Khan
Sales Associate in Sales
USA
Invespy
Heba Fareed Saleh Khas heba@invespy.com Reports to Owais Khan
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 55 212 9713
Alina Kindyakova alina@invespy.com Reports to Owais Khan
Channel Relationship Manager in
Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971 521577559
Arpit Kohli arpit@invespy.com Reports to Rashmi Kapale
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
0588581196
A Reports to Ahmed Agiza tash Kulkarni atash@invespy.com
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 13/23
L
M
FP&A Manager in Finance
Dubai - Head Office | 3:23 PM local
time
PIXL
588853343
504312784
Suman Kumari suman@pixl.ae Reports to Imran Khan
7 direct reports
Email Marketing Specialist in Email
Marketing and Data Analytics
Philippines
PIXL
Luwi Limbo luwi@pixl.ae Reports to Saloni Rohatgi
Relationship Manager in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971544051828
Pershant Lohana pershant@invespy.com Reports to Stuart Flynn
Creative Director in Creative
Dubai - Head Office | 3:23 PM local
time
PIXL
+971 52 933 5855
Reports to Pierre Van der
Merwe
Julio Luengo julio@pixl.ae
Public Relations Manager in PR
Dubai - Head Office | 3:23 PM local
time
PIXL
+971 58 568 9909
Reports to Debanjana
Chaudhuri
Donna Mackin donna@pixl.ae
Relationship Manager in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
971561133885
Melanie Mag-Aso melanie@invespy.com Reports to Owais Khan
Project Manager in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971 54 715 3112
Henry Martin henry@invespy.com Reports to Owais Khan
2 direct reports
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 14/23
Administrator in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971509325647
Stacy Matilla stacy@invespy.com Reports to Owais Khan
Talent Acquisition Lead in Human
Resources
Dubai - Head Office | 3:23 PM local
time
PIXL
+971585075381
Shauna Mc Dermott shauna@pixl.ae Reports to Rashmi Kapale
Relationship Manager in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971503811090
Nadia Megtit nadia@invespy.com Reports to Stuart Flynn
Tele Sales Executive in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971 50 819 5056
Seblewengel Mengiste seblewengel@invespy.com Reports to Amogh Desmukh
Project Manager in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971559997343
Toby Mishon toby@invespy.com Reports to Owais Khan
5 direct reports
Senior Manager- Commercial
Excellence in Sales
Dubai - Head Office | 3:23 PM local
time
PIXL
588853593
Reports to Nishanth
Kakkamani
Arjun Mitawalkar arjun@pixl.ae
Accounts Executive in Finance
Dubai - Head Office | 3:23 PM local
time
PIXL
+971 56 886 9551
Aswanth Mk aswanth@pixl.ae Reports to Suman Kumari
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 15/23
N
Head of Client Success in Account
Management
Dubai - Head Office | 3:23 PM local
time
PIXL
+971563986454
Omnia Mohammed omnia@pixl.ae Reports to Imran Khan
4 direct reports
Content Creator in Content
Dubai - Head Office | 3:23 PM local
time
PIXL
0508468055
0525209955
Reports to Pierre Van der
Merwe
Habeeb Mohammed Ismail habeeb@pixl.ae
1 direct report
Managing Partner in Business
Development
Dubai -Other location | 3:23 PM
local time
Quattro
Mohammad Motavasel mm@quattro-capital.com 1 direct report
Traffic Manager in Creative
Dubai - Head Office | 3:23 PM local
time
PIXL
+9715830204896
+27718668490
Reports to Pierre Van der
Merwe Mary Motubatse mary@pixl.ae
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971585981217
Ellie Mousavi ellie@invespy.com Reports to Sherief Aslan
Administrator in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 545451503
+971 528459500
Nayab Mumtaz nayab@invespy.com Reports to Owais Khan
Senior Copywriter in Content
Dubai - Head Office | 3:23 PM local
time
PIXL
+971586921800
+256772571800
Reports to Azra Sulthana Ivan Musoke ivan@pixl.ae
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 16/23
O
P
Relationship Manager in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971 56 729 2840
Yasser Najaar yasser@invespy.com Reports to Amogh Desmukh
Administrator in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971526364574
Julie Ann Narito julie@invespy.com Reports to Owais Khan
Technical Project Lead in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
057114541
Muhammad Navaid navaid@invespy.com Reports to Saloni Rohatgi
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 50 488 4822
Sameh Nooh sameh@invespy.com Reports to Mubeen Iqbal
Accounting and Admin Executive in
Finance
Dubai - Head Office | 3:23 PM local
time
PIXL
Shenna Ocay shenna@pixl.ae Reports to Suman Kumari
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 56 159 1153
Samiya Oubrahim samiya@invespy.com Reports to Michael Masri
Senior Account Executive in Account
Management
Dubai - Head Office | 3:23 PM local
time
PIXL
Vishwa Patni vishwa@pixl.ae Reports to Mansi Patel
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 17/23
R
Graphic Designer in Design
Dubai - Head Office | 323 PM local
time
PIXL
971 525361658
Monica Pawar monica@pixl.ae Reports to Fahad Khan
OUT DEC 4-12
Pre-Sales Executive in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
562791990
Dheerka Pradeep Nishantha De Alwis dheerka@invespy.com Reports to Amogh Desmukh
Graphic Designer in Marketing
Pakistan
PIXL
+923110484180
Mouzam Rahman mouzam@pixl.ae Reports to Saloni Rohatgi
Head of Technology in Technology
Group
India | 4:53 PM local time
Technology Group
+916385528531
+916385528531
Venkatesan Rajagopal venky@pixl.ae Reports to Imran Khan
3 direct reports
Senior Communications Strategist
in PR
Dubai - Head Office | 3:23 PM local
time
PIXL
+971 56 822 1395
Reports to Debanjana
Chaudhuri
Shweta Ramesh shweta@pixl.ae
Project Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971585887871
Navid Rashid navid@invespy.com Reports to Owais Khan
2 direct reports
Product Director Invespy in Email
Marketing and Data Analytics
Dubai - Head Office | 3:23 PM local
time
Technology Group
0525601824
Saloni Rohatgi saloni@pixl.ae Reports to Imran Khan
8 direct reports
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 18/23
S
Relationship Manager in Invespy
Dubai - Head Office | 3:23 PM local
time
Invespy
+971545204415
Elaine Rubiso elaine@invespy.com Reports to Stuart Flynn
Accounts Executive in Finance
Dubai - Head Office | 3:23 PM local
time
PIXL
+971564519871
Ravikant Runthla ravikant@pixl.ae Reports to Suman Kumari
Project Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 58 520 5829
0585205829
Zonja Rust zonja@invespy.com Reports to Owais Khan
3 direct reports
Senior Designer in Creative
Dubai - Head Office | 323 PM local
time
Creative
971523205565
Reports to Pierre Van der
Merwe
Ahla Saeed ahla@pixl.ae
OUT DEC 1-17
Talent Acquisition Executive in
Human Resources
Dubai -Other location | 3:23 PM
local time
PIXL
+971 58 592 9885
Gie Santos angeline@pixl.ae Reports to Rashmi Kapale
Graphic Designer in Creative
Dubai - Head Office | 3:23 PM local
time
PIXL
+971561711149
Reports to Pierre Van der
Merwe
Jomark Sanvicente joseph.s@pixl.ae
Head of Growth Marketing in
Marketing
Dubai - Head Office | 3:23 PM local
time
PIXL
+971 58 953 7400
Prasad Sawant prasad@pixl.ae Reports to Imran Khan
4 direct reports
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 19/23
Graphic Designer in Content
Pakistan
PIXL
+923321664819
+923321664819
Rida Sehr Reports to Azra Sulthana ish rida@pixl.ae
Account Executive in Account
Management
Dubai - Head Office | 3:23 PM local
time
PIXL
Revanth Selvan revanth@pixl.ae Reports to Jamie Donovan
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 54 500 8839
Zain Shah zain@invespy.com Reports to Zonja Rust
Graphic Designer in Creative
Pakistan
PIXL
+923125381072
+923125381072
Saad Shakoor saad@pixl.ae Reports to Fahad Khan
Product Designer in Technology
Group
India | 4:53 PM local time
Technology Group
+919047119115
Reports to Venkatesan
Rajagopal
Ramadevan Shanmugam ram@pixl.ae
Data Analyst in Email Marketing and
Data Analytics
Gurgaon, India | 4:53 PM local time
Technology Group
8439803044
Shiva Sharma shiva@pixl.ae Reports to Saloni Rohatgi
OUT DEC 4-16
Project Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971561132499
0561105058
Alaa Shkier alaa.s@invespy.com Reports to Owais Khan
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 20/23
T
Administrator in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 56 936 9454
Marifi Silvestre marifi@invespy.com Reports to Owais Khan
Paid Media Manager in Performance
Gurgaon, India | 4:53 PM local time
PIXL
9654000830
7015235054
Amar Reports to Prasad Sawant jeet Singh amarjeet@pixl.ae
OUT DEC 10-12
Business Development Manager in
Sales
Dubai - Head Office | 323 PM local
time
PIXL
Reports to Nishanth
Kakkamani
Liwaa Sleit liwaa@pixl.ae
OUT DEC 8-19
PR Executive in PR
Dubai - Head Office | 323 PM local
time
PIXL
0542484775
Reports to Debanjana
Chaudhuri
Pranjali Somase pranjali@pixl.ae
OUT DEC 11-12
Marketing Manager in Marketing
Dubai - Head Office | 3:23 PM local
time
Invespy
+971 52 329 9339
Savita Sood savita@invespy.com Reports to Saloni Rohatgi
Head of Content in Content
Dubai - Head Office | 3:23 PM local
time
Creative
0585946548
Reports to Pierre Van der
Merwe
Azra Sulthana azra@pixl.ae
8 direct reports
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971581782588
Aleksandra Taybulatova aleksandra@invespy.com Reports to Zonja Rust
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 21/23
V
Tele Sales Executive in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 52 791 0103
Priya Thul priya@invespy.com Reports to Amogh Desmukh
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971585199803
Nicola Tomanic nicola@invespy.com Reports to Zonja Rust
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 58 828 0270
Larissa Tsapousto larissa@invespy.com Reports to Toby Mishon
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 54 771 1911
Ahmad Ali turkman ahmad@invespy.com Reports to Sherief Aslan
Executive Creative Director in
Creative
Dubai - Head Office | 3:23 PM local
time
PIXL
+971 551230394
Pierre Van der Merwe pierre@pixl.ae Reports to Imran Khan
8 direct reports
Events Executive in Events
Dubai - Head Office | 323 PM local
time
PIXL
Ivana Van Heer ivana@pixl.ae Reports to Rashmi Kapale
OUT DEC 3-19
Sales Manager in Invespy
Dubai -Other location | 3:23 PM
local time
Invespy
+971 50 993 9185
Veranika Varabei veranika@invespy.com Reports to Owais Khan
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 22/23
12/11/25, 3:23 PM Directory: Quick Access
https://pixl.bamboohr.com/anytime/directory.php 23/23
"""

def parse_directory_text():
    print("--- PARSING DIRECTORY TEXT ---")
    
    # 1. Regex Strategy for Name/Email Line
    # Looks for:  Name  Email  Reports to...
    # Name can be multiple words. Email is standard.
    # Note: Sometimes there is junk before name like "reports to..." on prev line
    
    # Regex for Email
    email_regex = re.compile(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
    
    # Regex for Phone (generous)
    # Starts with +971 or 05 or 971 or +91 etc.
    phone_regex = re.compile(r'^(\+?(?:971|91|92|964|27|965|00971)?\s?0?5\d[\d\s-]{6,})$')
    
    lines = [L.strip() for L in DIRECTORY_TEXT.split('\n') if L.strip()]
    
    count_created = 0
    count_existing = 0
    count_updated = 0
    
    # We iterate and look for Email as anchor
    for i, line in enumerate(lines):
        email_match = email_regex.search(line)
        if email_match:
            email = email_match.group(1)
            
            # Extract Name: Text before Email
            # Example: "Mohammad Jabed Aalam jabed@invespy.com Reports to..."
            # Split by email, take first part
            pre_email_text = line.split(email)[0].strip()
            
            # Sometimes parsing artifact: "Reports to Nishanth\nKakkamani\nAbdullah Al-Mohammedi abdullah..."
            # If pre_email_text is empty, name might be on prev line?
            # But looking at data, name is always on same line.
            
            name = pre_email_text
            
            # Clean up name if it has "Reports to " inside (unlikely if formatting holds)
            # But check if name is suspiciously long or contains known garbage
            
            if not name:
                continue

            # --- SEARCH BACKWARDS FOR METADATA ---
            phone = ''
            designation = ''
            
            # Look back up to 8 lines
            start_scan = max(0, i - 10)
            scan_lines = lines[start_scan:i]
            scan_lines.reverse() # Look from closest line upwards
            
            # 1. Phone: Usually immediate lines above
            # Scan until we hit something that is clearly NOT a phone (like a company name "PIXL")
            for p_line in scan_lines:
                # Clean line for phone regex
                clean_p = p_line.strip()
                if phone_regex.match(clean_p) or (len(clean_p) >= 9 and clean_p.replace(' ','').isdigit()):
                     # Found a phone. If we already have one, append?
                     # Some have multiple. Let's just take the first one found (the last one printed)
                     if not phone:
                         phone = clean_p
                elif "PIXL" in p_line or "Invespy" in p_line or "Quattro" in p_line or "Directory:" in p_line:
                    # Hit company/header anchor, stop looking for phone
                    pass
                else:
                    # Could be location, time, etc.
                    pass
            
            # 2. Designation: Usually the "First" line of the block.
            # How to define block start? 
            # Blocks seem separated by "Reports to..." of previous block? No.
            # But Titles often contain " in ". e.g. "Senior Accountant in Finance"
            # Or just text.
            # Let's rely on the fact that Title is generally 4-6 lines up.
            # Heuristic: Find line containing " in " that is NOT "Reports to".
            
            for p_line in scan_lines:
                if " in " in p_line and "Reports to" not in p_line and "@" not in p_line:
                    parts = p_line.split(" in ")
                    potential_title = parts[0].strip()
                    # Sanity check length
                    if len(potential_title) < 50:
                        designation = potential_title
                        break # Found it
            
            # --- DB ACTION ---
            # Check exist by Email
            contact = Contact.objects.filter(email=email).first()
            if not contact and phone:
                contact = Contact.objects.filter(phone_number__icontains=phone.replace(' ','')[-7:]).first() # Fuzzy phone match
                
            if contact:
                # Update?
                print(f"[EXISTS] {name} ({email})")
                
                changed = False
                if not contact.designation and designation:
                    contact.designation = designation
                    changed = True
                if not contact.phone_number and phone:
                     contact.phone_number = phone
                     changed = True
                     
                if changed:
                    contact.save()
                    count_updated += 1
                    print(f"   -> Updated details")
                
                count_existing += 1
            else:
                Contact.objects.create(
                    name=name,
                    email=email,
                    phone_number=phone,
                    designation=designation
                )
                print(f"[CREATED] {name}")
                count_created += 1

    print(f"\n--- PARSE COMPLETE ---")
    print(f"Created: {count_created}")
    print(f"Updated: {count_updated}")
    print(f"Existing (Skipped): {count_existing}")

if __name__ == '__main__':
    parse_directory_text()
