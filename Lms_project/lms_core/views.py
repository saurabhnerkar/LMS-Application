from django.shortcuts import render
import random

def home(request):
  
    marketing_courses = [
        {
            "name": "Full Stack Java Development with AI",
            "description": "Learn modern Java stack with industry projects.",
            "image": "/static/images/java.png",
            "url": "#"
        },
        {
            "name": ".NET Developer Bootcamp",
            "description": "Everything you need for enterprise .NET.",
            "image": "/static/images/dotnet.png",
            "url": "#"
        },
        {
            "name": "Python Data Science",
            "description": "Master Python for data analytics and ML.",
            "image": "/static/images/python.png",
            "url": "#"
        },
        # Add more marketing courses...
    ]

    # Random/static testimonials and success stories
    testimonials = [
        {
            "name": "Tithi Suryawanshi",
            "achievement": "Placed at 5.5 LPA",
            "copy": "Highly recommended for learning and career growth.",
            "image": "/static/images/tithi.jpg"
        },
        {
            "name": "Ashwini Chavare",
            "achievement": "Secured as HR Executive at 4.5 LPA",
            "copy": "Excellent support and training at ITPRENEUR.",
            "image": "/static/images/ashwini.jpg"
        },
        # Add more...
    ]
    # Shuffle for random display
    random.shuffle(testimonials)

    context = {
        "marketing_courses": marketing_courses,
        "testimonials": testimonials[:4],  # Show top 4 each time
    }
    return render(request, "home.html", context)
