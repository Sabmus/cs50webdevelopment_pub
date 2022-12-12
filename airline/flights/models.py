from django.db import models


# Create your models here.
class Airport(models.Model):
    code = models.CharField(max_length=3)
    city = models.CharField(max_length=64)

    def __str__(self) -> str:
        return f"{self.city} ({self.code})"


class Flight(models.Model):
    # if I'm an Airport, I want to check every flight that has me as origin
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    # if I'm an Airport, I want to check every flight that has me as destination
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    duration = models.IntegerField()
    
    def __str__(self) -> str:
        return f"{self.id}: {self.origin} to {self.destination}"

    def is_valid_flight(self):
        return self.origin != self.destination and self.duration > 0


class Passenger(models.Model):
    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64)
    flights = models.ManyToManyField(Flight, blank=True, related_name="passengers")  # blank=True means that a passenger has no flight

    def __str__(self) -> str:
        return f"{self.first} {self.last}"
