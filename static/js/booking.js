function bookConsultation(mentorId){

fetch("/api/consultations/",{

method:"POST",

headers:{
"Content-Type":"application/json",
"Authorization":"Bearer "+localStorage.getItem("access_token")
},

body:JSON.stringify({

mentor: mentorId,
date:"2026-03-20",
time:"15:00"

})

})
.then(res => res.json())
.then(data => {

 alert(typeof t === 'function' ? t('booking.success', 'Consultation booked!') : 'Consultation booked!')

})

}
