import java.io.File;
import java.nio.file.*;
import com.android.tools.smali.baksmali.*;
import com.android.tools.smali.dexlib2.*;
import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.dexlib2.writer.builder.*;
import com.android.tools.smali.dexlib2.writer.io.*;
import brut.androlib.src.SmaliBuilder;

public class DexTool {
    public static void main(String[] args) throws Exception {
        Path input = Path.of(args[1]);
        if (args[0].equals("decode")) {
            var dex = new DexBackedDexFile(null, Files.readAllBytes(input), 0);
            Baksmali.disassembleDexFile(dex, new File(args[2]), 2, new BaksmaliOptions());
        } else {
            var builder = new DexBuilder(new Opcodes(28, -1));
            var smali = new SmaliBuilder(input.toFile(), 28);
            try (var paths = Files.walk(input)) {
                for (Path file : paths.filter(p -> p.toString().endsWith(".smali")).toList())
                    smali.buildFile(input.relativize(file).toString(), builder);
            }
            builder.writeTo(new FileDataStore(new File(args[2])));
        }
    }
}
