package vm;

import java.io.*;
import java.net.*;
import java.nio.*;
import java.lang.reflect.*;

/** VM-only raw framebuffer stream. No encoder, file writes, or APK modification. */
public final class ScreenStream {
    public static void main(String[] args) throws Exception {
        int width = args.length > 0 ? Integer.parseInt(args[0]) : 960;
        int height = args.length > 1 ? Integer.parseInt(args[1]) : 540;
        int fps = args.length > 2 ? Integer.parseInt(args[2]) : 3;
        if (width < 320 || width > 1280 || height < 180 || height > 720)
            throw new IllegalArgumentException("Unsupported preview dimensions");
        if (fps < 1 || fps > 10) throw new IllegalArgumentException("Unsupported frame rate");
        long interval = 1000 / fps;
        Class<?> surface = Class.forName("android.view.SurfaceControl");
        Class<?> rect = Class.forName("android.graphics.Rect");
        Class<?> bitmap = Class.forName("android.graphics.Bitmap");
        Class<?> config = Class.forName("android.graphics.Bitmap$Config");
        Method screenshot = surface.getDeclaredMethod("screenshot", rect,
                int.class, int.class, int.class);
        screenshot.setAccessible(true);
        Object crop = rect.getConstructor().newInstance();
        Method getWidth = bitmap.getMethod("getWidth");
        Method getHeight = bitmap.getMethod("getHeight");
        Method copy = bitmap.getMethod("copy", config, boolean.class);
        Method pixels = bitmap.getMethod("copyPixelsToBuffer", Buffer.class);
        Method recycle = bitmap.getMethod("recycle");
        Object argb = config.getField("ARGB_8888").get(null);
        ServerSocket server = new ServerSocket(38582, 1, InetAddress.getByName("127.0.0.1"));
        System.out.println("VM frame stream ready on loopback:38582");
        while (true) {
            try (Socket socket = server.accept()) {
                socket.setTcpNoDelay(true);
                DataOutputStream out = new DataOutputStream(new BufferedOutputStream(socket.getOutputStream(), 262144));
                ByteBuffer buffer = null;
                while (!socket.isClosed()) {
                    long started = System.nanoTime();
                    Object hardware = screenshot.invoke(null, crop, width, height, 0);
                    if (hardware == null) { Thread.sleep(100); continue; }
                    Object software = copy.invoke(hardware, argb, false);
                    recycle.invoke(hardware);
                    if (software == null) throw new IOException("Bitmap copy returned null");
                    int w = (Integer)getWidth.invoke(software);
                    int h = (Integer)getHeight.invoke(software);
                    int size = w*h*4;
                    if (buffer == null || buffer.capacity() != size) buffer = ByteBuffer.allocate(size);
                    buffer.clear();
                    pixels.invoke(software, buffer);
                    recycle.invoke(software);
                    out.writeInt(0x414c5631);
                    out.writeInt(w); out.writeInt(h); out.writeInt(size);
                    out.write(buffer.array()); out.flush();
                    long ms = (System.nanoTime()-started)/1000000;
                    if (ms < interval) Thread.sleep(interval-ms);
                }
            } catch (Throwable error) {
                error.printStackTrace();
                Thread.sleep(500);
            }
        }
    }
}
