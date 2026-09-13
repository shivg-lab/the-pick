from app.models.domain import EventWeather, EvidenceItem


def attire_suggestions(weather: EventWeather, rules: list[EvidenceItem]) -> list[str]:
    tips = []
    if weather.status == "available":
        low, high = weather.feels_like_min_f, weather.feels_like_max_f
        if low is not None and low < 50:
            tips.append("It may feel cold outdoors: wear a warm jacket over layers.")
        elif low is not None and low < 65:
            tips.append(
                "It may feel cool outdoors: bring a sweater or light jacket you can put on as temperatures drop."
            )
        elif high is not None and high >= 80:
            tips.append(
                "It may feel warm outdoors: choose lightweight, breathable clothing; consider a hat and sunglasses for time in the sun."
            )
        else:
            tips.append("A light, removable layer should give you flexibility while outdoors.")
        if low is not None and high is not None and low < 65 and high >= 80:
            tips.append("The forecast also includes warmer hours: wear a breathable base layer under your jacket.")
        if weather.rain_probability_max is None:
            tips.append("Rain probability is unavailable. Check precipitation before choosing your outer layer.")
        elif weather.rain_probability_max >= 30:
            tips.append("Rain is possible during the planning window: pack a rain jacket or poncho for time outdoors.")
            if any(
                e.freshness == "current"
                and isinstance(e.value, dict)
                and e.value.get("umbrella_use") in {"restricted", "prohibited"}
                for e in rules
            ):
                tips.append(
                    "The stored venue rules restrict umbrella use, so a wearable rain layer is the more practical choice. See the exact restrictions below."
                )
        if weather.wind_max_mph is not None and weather.wind_max_mph >= 15:
            tips.append("Breezy conditions are forecast: consider a wind-resistant outer layer.")
    else:
        tips.append("Wear comfortable walking shoes and bring a removable layer.")
        tips.append(
            "An event-time forecast is not available here yet. Check the forecast before choosing warmer or rain-ready layers."
        )
    if weather.status == "available":
        tips.append("Choose comfortable walking shoes. Outdoor forecasts do not predict indoor seating temperatures.")
    # Preserve every sourced restriction (including conflicts) instead of interpreting prose as permissions.
    if rules:
        tips.append(
            "Check the clothing and umbrella rules below before packing."
        )
    else:
        tips.append(
            "Venue-specific clothing and umbrella requirements are not verified. Check the official event guide before packing."
        )
    return tips
