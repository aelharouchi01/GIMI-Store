/* Shared testimonial slider for the standalone landing pages.
   A <div class="tslider" data-testi="cip"></div> auto-mounts on load.
   Mirrors the cert-detail modal sliders in index.html. */
(function () {
  var DATA = {
    cip: [
      { q: "The University of Charleston Innovation team has long held that anyone and everyone can innovate. The CIP Level 1 and Level 2 programs gave us the framework and processes to actually show our students and clients HOW to innovate.", n: "David Ramsburg", r: "Executive Director of Innovation, University of Charleston" },
      { q: "I sought a transparent, proven, and tested innovation process to understand and explain. The Certified Innovation Professional program did just that, delivered by qualified and experienced educators and mentors.", n: "Dr. Antoine Musu", r: "Faculty Lecturer, University of Western Australia" },
      { q: "The course was engaging and interactive. Hitendra's insights were valuable and deepened my understanding of innovation. I enjoyed the practical applications and real-world examples.", n: "Inva Xhafa", r: "Portfolio Risk Data Analyst, Allianz" },
      { q: "What I loved most was how it gave me a fresh perspective on approaching challenges and ideas. The mentors were amazing, and connecting with other participants was incredibly inspiring.", n: "Ledia Myzeqari", r: "FP&A, Abbott" },
      { q: "There's more to innovation than I'd imagined, and I'm thankful for discovering GIMI and their CIP program. I gave the certificate my whole time and effort, and it definitely paid off.", n: "Mario Nehme", r: "Operation Control Officer, LAVAJET" },
      { q: "I appreciated the structured approach to innovation. The course provided practical tools and frameworks that can be directly applied to real-world challenges, with engaging activities that encouraged creative thinking.", n: "Tahani Al Yammahi", r: "Certified Innovation Professional" },
      { q: "The CIP certificate provides knowledge based on a globally developed framework. My mindset has changed and my view has opened to being able to innovate, learning the power of innovation in a team setting.", n: "Yushry Ally", r: "Certified Innovation Professional" },
      { q: "It wasn't just about mastering innovation; it was a journey that made an impression. Learning alongside international professionals gave me a unique narrative to share with aspiring Filipino innovators.", n: "Randell Ramirez", r: "Certified Innovation Professional · Philippines" },
      { q: "This certification comes with a set of powerful tools and concepts that can be applied basically anywhere and at any level of the organization.", n: "Ernie Zainie", r: "Sr. Corporate Strategy Manager, Sabah Electricity" },
      { q: "This certificate is an open door to disruption for workplaces that aspire to be the best and want to make things happen.", n: "Lenin Causil", r: "Quality Management Coordinator, Aguas de Cartagena" }
    ],
    ccio: [
      { q: "The CCIO Certification (Level 4) let me view innovation holistically and understand the end-to-end connections across its four pillars: Strategy, Capacity, Discipline, and Performance. The journey from Level 1 to Level 4 has been transformative.", n: "Aakash Handa", r: "Foresight Planning & Innovation Unit Head, DCT Abu Dhabi" },
      { q: "We are grateful for the invaluable knowledge and skills gained through the Certified Chief Innovation Officer program. The material, methodology, and case studies are all exceptional, with a practical approach and real-world applications.", n: "Prakash Anantharaman", r: "VP Research & Advanced Engineering, Renault Nissan" },
      { q: "This journey has been a learning and rewarding experience. I look forward to applying these skills to drive meaningful change and foster a culture of innovation worldwide.", n: "Kalpana Majumdar", r: "Data Glue Consulting" },
      { q: "The CCIO program offers a rigorous yet practical innovation framework, from defining 'why' and 'where' to executing impact, empowering you to confidently turn ideas into measurable results over a 6-8 month journey.", n: "Raid Alghamdi", r: "General Authority for Competition" },
      { q: "If I had a euro for every 'aha!' moment during this intensive course, I'd be buying my own tech-innovation lab by now. I'm now certified to turn ideas into purposeful strategy and connected to a huge like-minded community.", n: "Akram Alhaddad", r: "Strategic Innovation Management" },
      { q: "The program was exceptionally well-organized. The knowledge and skills I've gained have been invaluable, and the interesting case studies truly made the learning process enjoyable and enriching.", n: "Brijesh Jha", r: "Deputy GM, Renault Nissan Technology & Business Centre India" },
      { q: "Innovation is a rapidly evolving field, and having the opportunity to learn directly from seasoned practitioners was crucial. Their hands-on expertise provided invaluable insights difficult to find in more theoretical programs.", n: "Meryem Serji", r: "Head of Innovation, OCP Nutricrops" },
      { q: "This credential reflects my commitment to driving innovation, digital transformation, and strategic value creation. Innovation is about turning ideas into impactful solutions that transform industries.", n: "Layla AlRawais", r: "Director, Digital Transformation & Strategy, Saudi Arabia Government" }
    ],
    cff: [
      { q: "The Future Foresight training workshop was an insightful and transformative experience that greatly enhanced my understanding of foresight methodologies and their practical applications.", n: "Khawaja Hammad Akbar", r: "Future Foresight participant" },
      { q: "This certification gives organizations a structured, systematic, future-oriented process to better prepare, motivate change, and enhance medium and long-term decision-making.", n: "Abdelrahman Zuraik", r: "Innovation & Entrepreneurship Director, Medical Village" },
      { q: "It is refreshing to learn methodical new ways to anticipate the future. I highly recommend this course for anyone future-proofing their organization.", n: "Abbie L. Abbott", r: "Regional HR & Admin Manager, Sia Partners" }
    ]
  };
  function mount(el, items) {
    if (!items || !items.length) return;
    var cards = items.map(function (t) {
      return '<div class="ts-card"><div class="ts-head"><div>' +
        '<div class="ts-n">' + t.n + '</div>' + (t.r ? '<div class="ts-r">' + t.r + '</div>' : '') +
        '</div></div><p>“' + t.q + '”</p></div>';
    }).join('');
    var nav = items.length > 3
      ? '<div class="ts-nav"><button class="ts-arrow" data-d="-1" aria-label="Previous">‹</button><button class="ts-arrow" data-d="1" aria-label="Next">›</button></div>' : '';
    el.innerHTML = '<div class="ts-track">' + cards + '</div>' + nav;
    var track = el.querySelector('.ts-track');
    function step() { var c = track.querySelector('.ts-card'); return c ? c.offsetWidth + 18 : 320; }
    el.querySelectorAll('.ts-arrow').forEach(function (b) {
      b.onclick = function () { track.scrollBy({ left: step() * (+b.getAttribute('data-d')), behavior: 'smooth' }); };
    });
  }
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.tslider[data-testi]').forEach(function (el) {
      mount(el, DATA[el.getAttribute('data-testi')]);
    });
  });
})();
