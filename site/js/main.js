/* ===== AI Growth Labs — Main JavaScript ===== */

// Mobile nav toggle
document.getElementById('navToggle')?.addEventListener('click',()=>{
  document.getElementById('navLinks').classList.toggle('open');
});

// Scroll nav background
window.addEventListener('scroll',()=>{
  const nav=document.getElementById('nav');
  if(nav)nav.style.background=window.scrollY>50?'rgba(2,6,23,0.97)':'rgba(2,6,23,0.85)';
});

// Animated counters
function animateCounters(){
  document.querySelectorAll('[data-count]').forEach(el=>{
    const target=parseInt(el.dataset.count);
    const suffix=el.dataset.suffix||'';
    let current=0;
    const step=target/50;
    const timer=setInterval(()=>{
      current+=step;
      if(current>=target){current=target;clearInterval(timer);}
      el.textContent=Math.floor(current)+(current>=target?'+':'');
    },30);
  });
}
const counterObserver=new IntersectionObserver((entries)=>{
  entries.forEach(e=>{if(e.isIntersecting){animateCounters();counterObserver.disconnect();}});
});
document.querySelectorAll('.hero-stats').forEach(el=>counterObserver.observe(el));

// FAQ accordion
document.querySelectorAll('.faq-q').forEach(q=>{
  q.addEventListener('click',()=>{
    const item=q.parentElement;
    const wasOpen=item.classList.contains('open');
    document.querySelectorAll('.faq-item').forEach(i=>i.classList.remove('open'));
    if(!wasOpen)item.classList.add('open');
  });
});

/* ===== CHATBOT ENGINE ===== */
const ChatBot={
  state:{step:0,data:{},typing:false},
  flow:[
    {msg:"Hi there! 👋 I'm the AI Growth Labs assistant. I help USA local businesses grow their online presence.\n\nHow can I help you today?",
     options:["I need help with SEO","I want more Google reviews","I need leads & customers","I want a free website audit"]},
    {msg:"Great choice! To better help you, could you tell me your business name?",input:true,field:"businessName"},
    {msg:"Thanks! What industry is your business in?",
     options:["Dentist","Lawyer","Restaurant","Plumber","HVAC","Medical Spa","Other"],field:"industry"},
    {msg:"And which city/state are you located in?",input:true,field:"location"},
    {msg:"Got it! Do you currently have a website?",
     options:["Yes, I have a website","No, I don't have one yet"],field:"hasWebsite"},
    {msg:null,dynamic:true}, // Dynamic based on website answer
    {msg:"Let me understand your current situation better. What's your biggest challenge right now?",
     options:["Not enough customers","Low Google ranking","Few/bad reviews","No social media presence","Competitors outranking me","All of the above"],field:"challenge"},
    {msg:null,dynamic:true}, // Dynamic recommendation
    {msg:"Would you like to speak with one of our SEO specialists? We can schedule a free strategy call or continue chatting here.",
     options:["Schedule a free call","Continue chatting","Send me the audit report"],field:"nextStep"},
    {msg:null,dynamic:true} // Final step
  ],

  init(){
    this.sendBot(this.flow[0].msg,this.flow[0].options);
  },

  sendBot(msg,options){
    const messagesEl=document.getElementById('chatMessages');
    if(!messagesEl)return;

    // Show typing indicator
    const typingEl=document.createElement('div');
    typingEl.className='chat-msg bot';
    typingEl.innerHTML='<div class="typing"><span></span><span></span><span></span></div>';
    messagesEl.appendChild(typingEl);
    messagesEl.scrollTop=messagesEl.scrollHeight;

    setTimeout(()=>{
      typingEl.remove();
      const msgEl=document.createElement('div');
      msgEl.className='chat-msg bot';
      msgEl.textContent=msg;
      messagesEl.appendChild(msgEl);

      if(options&&options.length){
        const optDiv=document.createElement('div');
        optDiv.className='chat-options';
        options.forEach(opt=>{
          const btn=document.createElement('button');
          btn.className='chat-option';
          btn.textContent=opt;
          btn.addEventListener('click',()=>{
            this.sendUser(opt);
            optDiv.remove();
          });
          optDiv.appendChild(btn);
        });
        messagesEl.appendChild(optDiv);
      }
      messagesEl.scrollTop=messagesEl.scrollHeight;
    },800+Math.random()*600);
  },

  sendUser(msg){
    const messagesEl=document.getElementById('chatMessages');
    const userEl=document.createElement('div');
    userEl.className='chat-msg user';
    userEl.textContent=msg;
    messagesEl.appendChild(userEl);
    messagesEl.scrollTop=messagesEl.scrollHeight;

    // Save data
    const currentFlow=this.flow[this.state.step];
    if(currentFlow&&currentFlow.field){
      this.state.data[currentFlow.field]=msg;
    }

    this.state.step++;
    this.processStep(msg);
  },

  processStep(userMsg){
    const step=this.state.step;
    const flow=this.flow[step];
    if(!flow)return;

    if(flow.dynamic){
      this.handleDynamic(step,userMsg);
    }else{
      this.sendBot(flow.msg,flow.options);
    }
  },

  handleDynamic(step,userMsg){
    const data=this.state.data;

    if(step===5){
      // After website question
      if(data.hasWebsite&&data.hasWebsite.includes("Yes")){
        this.sendBot("Could you share your website URL? I can give you a quick assessment of your current SEO health.",null);
        this.flow[5]={msg:null,input:true,field:"websiteUrl",dynamic:false};
        // Re-process
        this.state.step=5;
        return;
      }else{
        this.sendBot("No worries! Having a website is the first step. We can help you build an SEO-optimized website that ranks on Google from day one.\n\nLet's continue to understand your needs better.");
        this.state.step++;
        setTimeout(()=>this.processStep(),1500);
        return;
      }
    }

    if(step===7){
      // Dynamic recommendation based on challenge
      const challenge=data.challenge||"growing online";
      let recommendation="";

      if(challenge.includes("customers")||challenge.includes("All")){
        recommendation=`Based on what you've told me about ${data.businessName||"your business"} in ${data.location||"your area"}, here's what I recommend:\n\n📍 Local SEO + GBP Optimization — to get you visible on Google Maps\n⭐ Reputation Management — to build trust with 5-star reviews\n📢 Targeted Google Ads — for immediate lead generation\n\nWe've helped similar ${data.industry||""} businesses increase leads by 300%+ in 3-6 months.`;
      }else if(challenge.includes("ranking")){
        recommendation=`For a ${data.industry||""} business in ${data.location||"your area"}, improving Google rankings requires our DNA-level approach:\n\n🔬 Full 12-Pillar SEO Audit — analyzing 100+ ranking factors\n📝 Content Strategy — targeting high-intent local keywords\n🔗 Authority Building — earning quality backlinks\n\nMost clients see page 1 rankings within 3-6 months.`;
      }else if(challenge.includes("reviews")){
        recommendation=`Reviews are crucial for ${data.industry||""} businesses! Here's our approach:\n\n⭐ Ethical Review Generation System — SMS + email + QR codes\n🛡️ Negative Review Response Framework\n📊 Reputation Monitoring Dashboard\n\nOur clients typically go from under 50 reviews to 500+ within 6 months.`;
      }else if(challenge.includes("social")){
        recommendation=`Social media presence is essential for ${data.industry||""} businesses. We offer:\n\n📱 Full Social Media Management — Instagram, Facebook, TikTok\n✍️ Daily Content Creation with AI tools\n📅 Strategic Posting Schedule for maximum engagement\n\nWe create 30 days of content in just 1 batch day.`;
      }else{
        recommendation=`Great news — we have exactly what ${data.businessName||"your business"} needs. As a ${data.industry||""} business in ${data.location||"your area"}, our AI-powered approach can help you overcome these challenges.\n\n📊 We'll start with a free DNA-level audit of your entire online presence.\n🎯 Then create a custom 90-day growth roadmap.\n📈 And execute with our proven strategies.`;
      }

      this.sendBot(recommendation);
      this.state.step++;
      setTimeout(()=>this.processStep(),2000);
      return;
    }

    if(step===9){
      // Final step
      const nextStep=data.nextStep||"";
      if(nextStep.includes("call")){
        this.sendBot("I'd love to connect you with our SEO specialist! 📞\n\nYou can:\n• Call us directly at (800) 555-0199\n• Or book a time that works for you:\n\n👉 Visit our contact page to schedule your free strategy call.\n\nWe'll review your audit results and create a custom plan for "+
        (data.businessName||"your business")+".\n\nAnything else I can help with?");
      }else if(nextStep.includes("audit")){
        this.sendBot("I'll prepare your free DNA-level SEO audit report! 📊\n\nTo send it, I'll need your email address. Could you share it?\n\nThe report will include:\n✓ Technical SEO analysis\n✓ Content quality score\n✓ Local SEO assessment\n✓ Competitor comparison\n✓ 90-day action plan\n\nYou'll receive it within 24 hours.");
        this.flow.push({msg:null,input:true,field:"email"});
        return;
      }else{
        this.sendBot("Perfect! Let me tell you more about our proven results. 🏆\n\n"+
        "We've helped 500+ USA businesses just like yours:\n"+
        "• 340% average traffic increase\n"+
        "• 3x average ROI\n"+
        "• 97% client retention rate\n\n"+
        "Our month-to-month contracts mean zero risk — we earn your trust every month.\n\n"+
        "Would you like me to walk you through our packages, or do you have specific questions?",
        ["Tell me about packages","I have a question","Get my free audit"]);
      }
      return;
    }

    // Handle email collection (if they chose audit report)
    if(data.email){
      this.sendBot("Thank you! 🎉 We'll send the complete DNA-level audit report for "+
      (data.businessName||"your business")+" to "+data.email+" within 24 hours.\n\n"+
      "The report includes actionable recommendations specific to "+
      (data.industry||"your industry")+" businesses in "+(data.location||"your area")+".\n\n"+
      "In the meantime, feel free to explore our case studies or ask me anything else!",
      ["View case studies","Ask another question"]);
    }
  }
};

// Chat UI handlers
document.getElementById('chatToggle')?.addEventListener('click',()=>{
  const chatbot=document.getElementById('chatbot');
  chatbot.classList.toggle('open');
  if(chatbot.classList.contains('open')&&!ChatBot.state.initialized){
    ChatBot.state.initialized=true;
    ChatBot.init();
  }
});

document.getElementById('chatClose')?.addEventListener('click',()=>{
  document.getElementById('chatbot').classList.remove('open');
});

document.getElementById('chatSend')?.addEventListener('click',()=>{
  const input=document.getElementById('chatInput');
  const msg=input.value.trim();
  if(msg){
    ChatBot.sendUser(msg);
    input.value='';
  }
});

document.getElementById('chatInput')?.addEventListener('keypress',(e)=>{
  if(e.key==='Enter'){
    const msg=e.target.value.trim();
    if(msg){
      ChatBot.sendUser(msg);
      e.target.value='';
    }
  }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(a=>{
  a.addEventListener('click',(e)=>{
    const target=document.querySelector(a.getAttribute('href'));
    if(target){e.preventDefault();target.scrollIntoView({behavior:'smooth',block:'start'});}
  });
});
