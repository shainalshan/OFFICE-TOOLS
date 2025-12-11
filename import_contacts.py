import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from contacts.models import Contact

VCF_DATA = """
BEGIN:VCARD
VERSION:3.0
FN:Mohammad Jabed Aalam
N:Aalam;Mohammad Jabed;;;
TEL;TYPE=CELL:0566409359
EMAIL:jabed@invespy.com
TITLE:Senior Accountant
ORG:Finance
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Rexi Abesekara
N:Abesekara;Rexi;;;
TEL;TYPE=CELL:526605885
EMAIL:rexi@pixl.ae
TITLE:Company Driver
ORG:CEO
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Prince Abongnuk
N:Abongnuk;Prince;;;
TEL;TYPE=CELL:+971 58 279 5769
EMAIL:prince@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Ayesha Aftab
N:Aftab;Ayesha;;;
EMAIL:ayesha@invespy.com
TITLE:Sales Associate
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Ahmed Agiza
N:Agiza;Ahmed;;;
TEL;TYPE=CELL:+971 589880925
EMAIL:ahmed@invespy.com
TITLE:Project Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Nikhil Agrawal
N:Agrawal;Nikhil;;;
TEL;TYPE=CELL:+971561669451
EMAIL:nikhil@pixl.ae
TITLE:FP & A Analyst
ORG:Finance
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Bilal Ahmad
N:Ahmad;Bilal;;;
EMAIL:bilal@pixl.ae
TITLE:Senior Designer
ORG:Creative
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Khaled Ahmed
N:Ahmed;Khaled;;;
TEL;TYPE=CELL:+971555201578
EMAIL:khaled@invespy.com
TITLE:Sales Executive
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Rizwan Ahmed
N:Ahmed;Rizwan;;;
TEL;TYPE=CELL:+971 55 961 9500
EMAIL:rizwan@invespy.com
TITLE:Tele Sales Executive
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Abdullah Al-Mohammedi
N:Al-Mohammedi;Abdullah;;;
TEL;TYPE=CELL:0562445541
EMAIL:abdullah.a@pixl.ae
TITLE:Manager- Business Growth & Client Relations
ORG:Sales
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Marah Alachkar
N:Alachkar;Marah;;;
TEL;TYPE=CELL:+971 50 124 5096
EMAIL:marah@pixl.ae
TITLE:Copywriter
ORG:Content
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Mohammad Albeetar
N:Albeetar;Mohammad;;;
TEL;TYPE=CELL:+971 58 164 1224
EMAIL:mohammad.a@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Naushad Ali
N:Ali;Naushad;;;
EMAIL:naushad@pixl.ae
TITLE:Senior Accountant
ORG:Finance
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Eugiel Alquizar
N:Alquizar;Eugiel;;;
TEL;TYPE=CELL:+971554679383
EMAIL:eugiel@invespy.com
TITLE:Administrator
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Rajakumari Ambati
N:Ambati;Rajakumari;;;
TEL;TYPE=CELL:+971 52 563 0860
EMAIL:rajakumari@pixl.ae
TITLE:Procurement Manager
ORG:Finance
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Karthik Anoop
N:Anoop;Karthik;;;
TEL;TYPE=CELL:+91 90619 30892
EMAIL:karthik@invespy.com
TITLE:Editor
ORG:Content
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Hamza Asad
N:Asad;Hamza;;;
TEL;TYPE=CELL:+971 55 746 5558
EMAIL:hamza@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Sherief Aslan
N:Aslan;Sherief;;;
EMAIL:Sherief@invespy.com
TITLE:Project Manager
ORG:Sales
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Azad Attar
N:Attar;Azad;;;
TEL;TYPE=CELL:+971 58 945 6493
EMAIL:azad@invespy.com
TITLE:Project Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Ryland Austria
N:Austria;Ryland;;;
TEL;TYPE=CELL:+971 50 464 9813
EMAIL:ryland@invespy.com
TITLE:Administrator
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Mandy Azzi
N:Azzi;Mandy;;;
TEL;TYPE=CELL:+96171001959
TEL;TYPE=CELL:0523462506
EMAIL:mandy@pixl.ae
TITLE:Social Media Manager - Content
ORG:Creative
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Binesh Babu
N:Babu;Binesh;;;
TEL;TYPE=CELL:0585463838
EMAIL:bpanicker@propertytime.ae
TITLE:CEO of Property Time
ORG:Property Time
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Nadiya Bacharni
N:Bacharni;Nadiya;;;
TEL;TYPE=CELL:+971526950030
EMAIL:nadiya@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Shainal Badusha
N:Badusha;Shainal;;;
TEL;TYPE=CELL:+971521374423
EMAIL:shainal@pixl.ae
TITLE:IT Executive
ORG:Operations
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Arjun Balagopal
N:Balagopal;Arjun;;;
TEL;TYPE=CELL:+971 58 580 0759
EMAIL:arjun.b@invespy.com
TITLE:Senior Manager - Channel Relationship
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Divya Balakrishnan
N:Balakrishnan;Divya;;;
TEL;TYPE=CELL:502882107
EMAIL:divya@pixl.ae
TITLE:Account Executive
ORG:Account Management
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Luliia Baranovska
N:Baranovska;Iuliia;;;
TEL;TYPE=CELL:+971 56 896 6388
EMAIL:iuliia@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Mounya Barich
N:Barich;Mounya;;;
TEL;TYPE=CELL:0527058673
EMAIL:mounya@invespy.com
TITLE:Channel Relationship Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Art Barrero
N:Barrero;Art;;;
TEL;TYPE=CELL:+971 55 974 3548
EMAIL:art@invespy.com
TITLE:Administrator
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Elnaz Barzegari
N:Barzegari;Elnaz;;;
EMAIL:elnaz@quattro-capital.com
TITLE:Relationship Manager
ORG:Sales
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Monisha Baskar
N:Baskar;Monisha;;;
TEL;TYPE=CELL:0565981697
EMAIL:Monisha@pixl.ae
TITLE:Media Manager
ORG:Sales
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Beah Beah
N:Beah;Beah;;;
TEL;TYPE=CELL:+971 56 730 0932
EMAIL:ahmed.b@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Venn Bedayo
N:Bedayo;Venn;;;
TEL;TYPE=CELL:+971502935501
EMAIL:wilven@invespy.com
TITLE:Sales Operations Executive
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Kate Benas
N:Benas;Kate;;;
TEL;TYPE=CELL:0554531740
EMAIL:kate@pixl.ae
TITLE:Receptionist/ Office Assistant
ORG:Human Resources
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Manahil Bhatti
N:Bhatti;Manahil;;;
TEL;TYPE=CELL:+971 56 909 5115
EMAIL:manahil@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Assia boudfel Boudfel
N:Boudfel;Assia boudfel;;;
TEL;TYPE=CELL:+971545393060
EMAIL:assia@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Carla Butler
N:Butler;Carla;;;
TEL;TYPE=CELL:+971 58 516 2658
EMAIL:carla@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Nancy Cabanillas
N:Cabanillas;Nancy;;;
TEL;TYPE=CELL:+971 50 348 1494
EMAIL:nancy@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Chazel Carnero
N:Carnero;Chazel;;;
EMAIL:chazel@pixl.ae
TITLE:Barista
ORG:Operations
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Alejandro Ceron
N:Ceron;Alejandro;;;
TEL;TYPE=CELL:+971 52 472 2404
EMAIL:alejandro@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Harshyy Chandwani
N:Chandwani;Harshyy;;;
TEL;TYPE=CELL:+971 58 588 7132
EMAIL:harshul@pixl.ae
TITLE:Content Creator
ORG:Creative
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Amer Chaudhary
N:Chaudhary;Amer;;;
TEL;TYPE=CELL:+971 58 667 0543
EMAIL:amer@invespy.com
TITLE:Director
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Debanjana Chaudhuri
N:Chaudhuri;Debanjana;;;
EMAIL:deb@pixl.ae
TITLE:Head- PR
ORG:PR
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Mike Cortiz
N:Cortiz;Mike;;;
EMAIL:mike@pixl.ae
TITLE:Office Boy
ORG:Operations
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Amogh Desmukh
N:Desmukh;Amogh;;;
TEL;TYPE=CELL:+971586748706
EMAIL:amogh@invespy.com
TITLE:Director
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Amitabh Dhawan
N:Dhawan;Amitabh;;;
TEL;TYPE=CELL:+971 50 580 1343
EMAIL:amitabh@invespy.com
TITLE:Director
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Gouthami Durgasi
N:Durgasi;Gouthami;;;
TEL;TYPE=CELL:+971 55 527 4699
EMAIL:gouthami@pixl.ae
TITLE:Marketing Executive
ORG:Marketing
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Lixx Edmund Madamesila
N:Madamesila;Lixx Edmund;;;
TEL;TYPE=CELL:+639672663595
EMAIL:felix@pixl.ae
TITLE:Data Integration Specialist
ORG:Integration and Tech Support
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Asmaa Elmahdy
N:Elmahdy;Asmaa;;;
TEL;TYPE=CELL:+971564237147
EMAIL:asmaa@invespy.com
TITLE:Tele Sales Executive
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Rawan Elsanoucy
N:Elsanoucy;Rawan;;;
TEL;TYPE=CELL:+971507031284
TEL;TYPE=CELL:+971507031294
EMAIL:rawan@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Nadine Elwakdy
N:Elwakdy;Nadine;;;
TEL;TYPE=CELL:+971 56 592 6728
EMAIL:nadine@pixl.ae
TITLE:Account Manager
ORG:Account Management
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Stuart Flynn
N:Flynn;Stuart;;;
TEL;TYPE=CELL:+971 54 402 5210
EMAIL:stuart@invespy.com
TITLE:Senior Manager - Channel Relationship
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Neha Gaba
N:Gaba;Neha;;;
EMAIL:neha@pixl.ae
TITLE:Digital Marketing Manager
ORG:Performance
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Jo dela Fuente Geronimo
N:Geronimo;Jo dela Fuente;;;
TEL;TYPE=CELL:0507341013
EMAIL:xyza@invespy.com
TITLE:Admin Executive
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Numan Ghani
N:Ghani;Numan;;;
TEL;TYPE=CELL:+923464449176
EMAIL:numan@pixl.ae
TITLE:Graphic Designer
ORG:Creative
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Haider Habib
N:Habib;Haider;;;
TEL;TYPE=CELL:0502564747
EMAIL:halder@pixi.ae
TITLE:Account Executive
ORG:Account Management
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Omer Hamid
N:Hamid;Omer;;;
EMAIL:omer@pixl.ae
TITLE:Business Systems Manager
ORG:Technology Group
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Kashmala Hattan
N:Hattan;Kashmala;;;
TEL;TYPE=CELL:+971526031024
EMAIL:kashmala@pixl.ae
TITLE:Social Media Designer
ORG:Creative
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Aruna Herath
N:Herath;Aruna;;;
TEL;TYPE=CELL:+971564995653
EMAIL:aruna@pixl.ae
TITLE:Video Content Creator
ORG:Content
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Marvie Hingpit
N:Hingpit;Marvie;;;
TEL;TYPE=CELL:+971545151887
EMAIL:marvie@invespy.com
TITLE:Administrator
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Urooj Husain
N:Husain;Urooj;;;
TEL;TYPE=CELL:0588853448
TEL;TYPE=CELL:0527769622
EMAIL:urooj@pixl.ae
TITLE:Director- Client Success
ORG:Account Management
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Taufique Hussain
N:Hussain;Taufique;;;
TEL;TYPE=CELL:+971 52 778 6643
EMAIL:taufique@invespy.com
TITLE:Tele Sales Executive
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Einas Ibrahim
N:Ibrahim;Einas;;;
TEL;TYPE=CELL:+971 55 659 7663
EMAIL:einas@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Fatima Imran
N:Imran;Fatima;;;
TEL;TYPE=CELL:+971504703009
EMAIL:fatima@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Mubeen Iqbal
N:Iqbal;Mubeen;;;
TEL;TYPE=CELL:+971521011370
EMAIL:mubeen@invespy.com
TITLE:Project Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Alaa Jabbour
N:Jabbour;Alaa;;;
TEL;TYPE=CELL:+971 56 600 5454
EMAIL:alaa@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Maria Jacob
N:Jacob;Maria;;;
TEL;TYPE=CELL:+971527812298
EMAIL:maria@pixl.ae
TITLE:Event Coordinator
ORG:Events
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Antigona Jahaj
N:Jahaj;Antigona;;;
TEL;TYPE=CELL:+971543100309
EMAIL:antigona@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Anshu Jain
N:Jain;Anshu;;;
TEL;TYPE=CELL:+971 58 588 7120
EMAIL:anshu@invespy.com
TITLE:Relationship Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Deepanshu Jangid
N:Jangid;Deepanshu;;;
TEL;TYPE=CELL:+919599174307
EMAIL:deepanshu@pixl.ae
TITLE:Paid Media Executive
ORG:Performance
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Lisha Jindal
N:Jindal;Lisha;;;
EMAIL:lisha@pixl.ae
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Carmen Joseph
N:Joseph;Carmen;;;
TEL;TYPE=CELL:9766188479
EMAIL:carmen@invespy.com
TITLE:FB Ads Specialist
ORG:Performance
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Prashant Joshi
N:Joshi;Prashant;;;
TEL;TYPE=CELL:+971 50 230 6980
EMAIL:prashant@pixl.ae
TITLE:Administrator
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Annie Justin
N:Justin;Annie;;;
TEL;TYPE=CELL:+971 52 508 5389
EMAIL:annie@invespy.com
TITLE:Relationship Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Ergena Kaci
N:Kaci;Ergena;;;
TEL;TYPE=CELL:+971 52 965 3567
EMAIL:ergena@invespy.com
TITLE:Sales Manager
ORG:Sales
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Nishanth Kakkamani
N:Kakkamani;Nishanth;;;
TEL;TYPE=CELL:+971522436879
EMAIL:nishanth@pixl.ae
TITLE:HR Business Partner
ORG:Human Resources
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Rashmi Kapale
N:Kapale;Rashmi;;;
TEL;TYPE=CELL:585255909
EMAIL:rashmi@pixl.ae
TITLE:Sales Manager
ORG:Sales
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Leyli Kazyohan
N:Kazyohan;Leyli;;;
TEL;TYPE=CELL:+971 58 540 8939
EMAIL:leyli@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Owais Khan
N:Khan;Owais;;;
TEL;TYPE=CELL:+971 50 160 5506
EMAIL:owais@invespy.com
TITLE:Director of Channel Relationships
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Mariam Khaled
N:Khaled;Mariam;;;
TEL;TYPE=CELL:+971 52 830 1864
EMAIL:mariam@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Amna Khan
N:Khan;Amna;;;
TEL;TYPE=CELL:052 825 8010
EMAIL:amna.k@invespy.com
TITLE:Relationship Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Owais Khan
N:Khan;Owais;;;
TEL;TYPE=CELL:+971 56 686 9899
EMAIL:owais.k@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Muhammad Khubaib
N:Khubaib;Muhammad;;;
TEL;TYPE=CELL:+971 50 873 2197
EMAIL:muhammad@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Waseem Koraishy
N:Koraishy;Waseem;;;
TEL;TYPE=CELL:+971 58 587 9110
EMAIL:Waseem@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Suman Kumari
N:Kumari;Suman;;;
TEL;TYPE=CELL:052 876 2552
EMAIL:suman@pixl.ae
TITLE:Senior Accountant
ORG:Finance
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Ahmed Lotfi
N:Lotfi;Ahmed;;;
TEL;TYPE=CELL:+971 55 580 0759
EMAIL:ahmed.l@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Ray Madrigal
N:Madrigal;Ray;;;
TEL;TYPE=CELL:+971 52 235 9180
EMAIL:ray@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Adnan Magrabi
N:Magrabi;Adnan;;;
TEL;TYPE=CELL:+971 58 596 0638
EMAIL:adnan@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Mariam Mahmoud
N:Mahmoud;Mariam;;;
TEL;TYPE=CELL:+971 50 200 8729
EMAIL:mariam.m@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Fathi Mallouli
N:Mallouli;Fathi;;;
TEL;TYPE=CELL:+971 52 268 8303
EMAIL:Fathi@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Jithin Manoharan
N:Manoharan;Jithin;;;
TEL;TYPE=CELL:+971 50 216 1137
EMAIL:Jithin@pixl.ae
TITLE:Head- SEO
ORG:Performance
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Yazeed Mansour
N:Mansour;Yazeed;;;
TEL;TYPE=CELL:+971 50 213 1999
EMAIL:yazeed@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Mohammad Mashkoor
N:Mashkoor;Mohammad;;;
TEL;TYPE=CELL:+971 52 642 7705
EMAIL:mashkoor@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Vasileios Matsoukas
N:Matsoukas;Vasileios;;;
TEL;TYPE=CELL:+971 58 565 1459
EMAIL:vasileios@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Jhoana Mayo
N:Mayo;Jhoana;;;
TEL;TYPE=CELL:058 518 9700
EMAIL:jhoana@invespy.com
TITLE:Sales Executive
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Toby Mishon
N:Mishon;Toby;;;
TEL;TYPE=CELL:+971 58 597 1010
EMAIL:toby@invespy.com
TITLE:Director of Sales
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Mohamed Mohsin
N:Mohsin;Mohamed;;;
TEL;TYPE=CELL:+971 58 586 2888
EMAIL:mohameed.m@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Shana Monaghan
N:Monaghan;Shana;;;
TEL;TYPE=CELL:+971 50 847 4522
EMAIL:shana@pixl.ae
TITLE:Marketing Executive
ORG:Marketing
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Jamil Motlaq
N:Motlaq;Jamil;;;
TEL;TYPE=CELL:+971 58 510 5233
EMAIL:jamil@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Khansa Mustapha
N:Mustapha;Khansa;;;
TEL;TYPE=CELL:+971 58 543 5431
EMAIL:Khansa@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Sara Nejad
N:Nejad;Sara;;;
TEL;TYPE=CELL:+971 58 594 7799
EMAIL:sara@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:John Omotosho
N:Omotosho;John;;;
TEL;TYPE=CELL:+971 52 491 5005
EMAIL:john@invespy.com
TITLE:Channel Relationship Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Shafi Padath
N:Padath;Shafi;;;
TEL;TYPE=CELL:+971 50 207 4333
EMAIL:shafi@pixl.ae
TITLE:SEO Strategist
ORG:Performance
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Surbhi Palta
N:Palta;Surbhi;;;
TEL;TYPE=CELL:056 612 0017
EMAIL:surbhi@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Nethra Palliyadi
N:Palliyadi;Nethra;;;
TEL;TYPE=CELL:+971 56 685 0229
EMAIL:nethra@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Naimul Hasan Patoary
N:Patoary;Naimul Hasan;;;
TEL;TYPE=CELL:+971 58 548 7695
EMAIL:naimul@pixl.ae
TITLE:Digital Marketing Executive
ORG:Performance
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Nethaji Paul
N:Paul;Nethaji;;;
TEL;TYPE=CELL:+971 56 680 7799
EMAIL:nethaji@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Anisha Payyoli
N:Payyoli;Anisha;;;
TEL;TYPE=CELL:+971 58 522 9314
EMAIL:anisha@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:V. N. R Priyadarshee
N:Priyadarshee;V. N. R;;;
TEL;TYPE=CELL:+971 58 586 1955
EMAIL:priyadarshee@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Sanchit Rai
N:Rai;Sanchit;;;
TEL;TYPE=CELL:+971 58 588 7136
EMAIL:sanchit@invespy.com
TITLE:Relationship Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Kedar Rajput
N:Rajput;Kedar;;;
TEL;TYPE=CELL:+971 58 588 7134
EMAIL:kedar@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Shami Rammohan
N:Rammohan;Shami;;;
TEL;TYPE=CELL:+971 50 148 4048
EMAIL:shami@pixl.ae
TITLE:Head - Finance
ORG:Finance
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Pradeep Rangan
N:Rangan;Pradeep;;;
TEL;TYPE=CELL:+971 56 686 9199
EMAIL:pradeep@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Hiba Raza
N:Raza;Hiba;;;
TEL;TYPE=CELL:+971 58 518 9700
EMAIL:hiba@invespy.com
TITLE:Sales Executive
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Laila Rustom
N:Rustom;Laila;;;
TEL;TYPE=CELL:+971 58 588 7130
EMAIL:laila@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Zonja Rust
N:Rust;Zonja;;;
TEL;TYPE=CELL:+971 58 597 1000
EMAIL:zonja@invespy.com
TITLE:Director of Sales
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Adnan Saeed
N:Saeed;Adnan;;;
TEL;TYPE=CELL:+971 58 588 7133
EMAIL:adnan.s@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Manju Santhosh
N:Santhosh;Manju;;;
TEL;TYPE=CELL:+971 58 512 8870
EMAIL:manju@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Asma Sarhan
N:Sarhan;Asma;;;
TEL;TYPE=CELL:+971 58 512 8870
EMAIL:asma@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Sara Sawsaf
N:Sawsaf;Sara;;;
TEL;TYPE=CELL:+971 58 178 2588
EMAIL:sarah@invespy.com
TITLE:Tele Sales Executive
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Aleksandra Taybulatova
N:Taybulatova;Aleksandra;;;
TEL;TYPE=CELL:+971 52 791 0103
EMAIL:aleksandra@invespy.com
TITLE:Tele Sales Executive
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Priya Thul
N:Thul;Priya;;;
TEL;TYPE=CELL:+971585199803
EMAIL:priya@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Nicola Tomanic
N:Tomanic;Nicola;;;
TEL;TYPE=CELL:+971 58 828 0270
EMAIL:nicola@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Larissa Tsapousto
N:Tsapousto;Larissa;;;
TEL;TYPE=CELL:+971 54 771 1911
EMAIL:larissa@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Ahmad Ali Turkman
N:Turkman;Ahmad Ali;;;
TEL;TYPE=CELL:+971 56 620 4404
EMAIL:ahmad@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Sherif Waziry
N:Waziry;Sherif;;;
TEL;TYPE=CELL:+971 50 119 5900
EMAIL:sherif@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Mariia Yeremieieva
N:Yeremieieva;Mariia;;;
TEL;TYPE=CELL:+971 58 554 1999
EMAIL:mariia@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Mahdi Younis
N:Younis;Mahdi;;;
TEL;TYPE=CELL:+971 58 588 7135
EMAIL:mahdi@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Zaid Zakri
N:Zakri;Zaid;;;
TEL;TYPE=CELL:+971 58 596 0528
EMAIL:zaid@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Zeinab Zein
N:Zein;Zeinab;;;
TEL;TYPE=CELL:+971 58 518 9700
EMAIL:zeinab@invespy.com
TITLE:Sales Manager
ORG:Invespy
END:VCARD
BEGIN:VCARD
VERSION:3.0
FN:Mariam Ziad
N:Ziad;Mariam;;;
TEL;TYPE=CELL:+971 58 518 9700
EMAIL:mariam.z@invespy.com
TITLE:Tele Sales Executive
ORG:Invespy
END:VCARD
"""

def parse_vcard(vcard_text):
    lines = vcard_text.strip().split('\n')
    data = {}
    
    for line in lines:
        if line.startswith('FN:'):
            data['name'] = line[3:].strip()
        elif line.startswith('TEL'):
            # Simple extraction for CELL/Work
            parts = line.split(':')
            if len(parts) > 1:
                data['phone_number'] = parts[1].strip()
        elif line.startswith('EMAIL'):
            parts = line.split(':')
            if len(parts) > 1:
                data['email'] = parts[1].strip()
        elif line.startswith('TITLE:'):
            data['designation'] = line[6:].strip()
            
    return data

def import_contacts():
    print("--- BULK IMPORTING CONTACTS ---")
    
    raw_cards = VCF_DATA.strip().split('END:VCARD')
    count = 0
    updated = 0
    
    for card in raw_cards:
        if 'BEGIN:VCARD' not in card:
            continue
            
        data = parse_vcard(card)
        
        name = data.get('name')
        if not name:
            continue
            
        # Get or Update logic
        # Identification key: Email (if exists) OR Phone OR Name
        # Priority: Email > Phone > Name (might be risky if name duplicates)
        
        contact = None
        
        if data.get('email'):
            contact = Contact.objects.filter(email=data['email']).first()
        
        if not contact and data.get('phone_number'):
            contact = Contact.objects.filter(phone_number=data['phone_number']).first()
            
        if not contact:
            contact = Contact.objects.filter(name=name).first()
            
        if contact:
            # Update fields if missing? Or overwrite? 
            # Prompt implies "add", so we might just ensure they exist. 
            # Let's update designation if it's new
            if 'designation' in data and data['designation'] != contact.designation:
                contact.designation = data['designation']
                contact.save()
                updated += 1
                print(f"[UPDATED] {name}")
            else:
                print(f"[SKIP] {name} already exists.")
        else:
            # Create
            Contact.objects.create(
                name=name,
                email=data.get('email', ''),
                phone_number=data.get('phone_number', ''),
                designation=data.get('designation', '')
            )
            count += 1
            print(f"[CREATED] {name}")

    print(f"\n--- IMPORT COMPLETE ---")
    print(f"Created: {count}")
    print(f"Updated: {updated}")

if __name__ == '__main__':
    import_contacts()
