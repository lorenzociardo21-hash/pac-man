class Solution:
    def maxArea(self, height: list[int]) -> int:
        water_potente = 0
        for i in range(len(height)):
            for e in range(len(height)):
                palo_piu_bass = height[i] if height[i] <= height[e] else height[i]
                water_try = palo_piu_bass * ((e+1) - (i+1))
                if water_try > water_potente:
                    water_potente = water_try
        return water_potente
