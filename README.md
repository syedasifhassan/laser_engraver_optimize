# laser_engraver_optimize
Cluster slices of an image together for better results when laser engraving.

# Context
When engraving images onto wood with a laser engraver, first the image must be sliced into paths for the laser to follow.  I found that sometimes the slices were visible in the finished result, but not when the laser had recently traveled nearby.

# Solution
I realized that if the surface was not allowed to cool in between passes, the rows would blend into one another more fully.  The trouble was that the laser was passing across the entire image with each slice, rather than staying in contiguous regions.  In my project, I was burning disconnected images onto multiple objects arranged in a grid, so it was especially amenable to separation of the overall image into discrete pieces.
So, I wrote a script to read the paths and rearrange the path segments into clusters that would be burned in groups.  The results were as expected, and striping across the images was no longer an issue.
